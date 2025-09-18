from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .. import auth, models
from ..schemas import PaymentOut, PaymentCreate
from datetime import datetime

router = APIRouter(prefix="/payments", tags=["payments"])

import qrcode
import os
import json
import uuid

@router.post("/", response_model=PaymentOut)
def create_payment(data: PaymentCreate, db: Session = Depends(auth.get_db), user: models.User = Depends(auth.get_current_user)):
    qrcode_hash = str(uuid.uuid4())  # 👈 Eşsiz QR kod hash’i üret

    payment = models.Payment(
        user_id=user.id,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        status="completed",
        created_at=datetime.utcnow(),
        event_id=data.event_id,
        qrcode_hash=qrcode_hash  # 👈 Hash’i veritabanına kaydet
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # QR kod verisi
    qr_data = {
        "payment_id": payment.id,
        "user_id": user.id,
        "event_id": payment.event_id,
        "qrcode_hash": qrcode_hash,  # 👈 Hash’i QR kod içine ekle
        "amount": payment.amount,
        "description": payment.description
    }
    qr_json = json.dumps(qr_data)
    qr = qrcode.make(qr_json)
    qr_dir = "uploads/qrcodes"
    os.makedirs(qr_dir, exist_ok=True)
    qr_path = os.path.join(qr_dir, f"payment_{payment.id}.png")
    qr.save(qr_path)
    payment.qrcode_path = qr_path
    db.commit()
    db.refresh(payment)

    return payment


@router.get("/qrcodes/{payment_id}")
def get_qrcode(payment_id: int, db: Session = Depends(auth.get_db), user: models.User = Depends(auth.get_current_user)):
    payment = db.query(models.Payment).get(payment_id)
    if not payment or payment.user_id != user.id:
        raise HTTPException(status_code=404, detail="QR code not found")
    if not payment.qrcode_path or not os.path.exists(payment.qrcode_path):
        raise HTTPException(status_code=404, detail="QR code file missing")
    return FileResponse(payment.qrcode_path, media_type="image/png")

@router.get("/validate/{payment_id}/{qrcode_hash}")
def validate_payment(payment_id: int, qrcode_hash: str, db: Session = Depends(auth.get_db), user = Depends(auth.get_current_user)):
    if user.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    payment = db.query(models.Payment).get(payment_id)
    if not payment:
        return {"valid": False, "message": "Payment not found"}

    if payment.qrcode_hash != qrcode_hash:
        return {"valid": False, "message": "QR code hash mismatch"}

    if payment.status != "completed":
        return {"valid": False, "message": "Payment not completed"}

    event = db.query(models.Event).get(payment.event_id)
    if not event:
        return {"valid": False, "message": "Event not found"}

    if user.role == "owner" and event.owner_id != user.id:
        return {"valid": False, "message": "This payment is not for your event."}

    if payment.used:
        return {"valid": False, "message": "This QR code has already been used."}

    payment.used = True
    db.commit()
    return {"valid": True, "message": "Payment confirmed and QR code marked as used."}


@router.get("/mytickets", response_model=List[PaymentOut])
def get_my_tickets(db: Session = Depends(auth.get_db), user = Depends(auth.get_current_user)):
    tickets = db.query(models.Payment).filter(models.Payment.user_id == user.id).all()
    return tickets
