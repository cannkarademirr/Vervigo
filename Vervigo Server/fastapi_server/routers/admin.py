from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from sqlalchemy.orm import Session
from .. import auth, models
from ..schemas import ApproveItem


router = APIRouter(prefix="/admin", tags=["admin"])

def admin_only(user: models.User = Depends(auth.get_current_user)):
    if user.role != 'admin': raise HTTPException(403)
    return user

@router.get('/queue')
def get_approved_queue(db: Session = Depends(auth.get_db), user = Depends(admin_only)):
    evs = db.query(models.Event).filter(models.Event.approved==False).all()
    bs = db.query(models.Business).filter(models.Business.approved==False).all()
    return {"events": evs, "businesses": bs}

@router.post('/approve')
def approve(item: ApproveItem, db: Session = Depends(auth.get_db), user = Depends(admin_only)):
    if item.type == 'event':
        obj = db.query(models.Event).get(item.id)
    else:  # business
        obj = db.query(models.Business).get(item.id)
        if obj:
            # business onaylanırsa owner kullanıcının rolünü değiştir
            owner = db.query(models.User).get(obj.owner_id)
            if owner and owner.role != "admin":
                owner.role = "owner"

    if not obj:
        raise HTTPException(404, "Item not found")
    obj.approved = True
    db.commit()
    return {"status": f"{item.type} {item.id} approved"}

@router.post('/reject')
def reject(item: ApproveItem, db: Session = Depends(auth.get_db), user = Depends(admin_only)):
    if item.type == 'event':
        obj = db.query(models.Event).get(item.id)
    else:  # business
        obj = db.query(models.Business).get(item.id)

    if not obj:
        raise HTTPException(404, "Item not found")

    db.delete(obj)
    db.commit()
    return {"status": f"{item.type} {item.id} rejected and deleted"}