from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, auth
import os
import uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/events", tags=["events"])

# Mount uploads directory for static file access
app = FastAPI()
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

def get_user(u = Depends(auth.get_current_user)): return u



@router.get('/', response_model=List[schemas.EventOut])
def show_events(
    db: Session = Depends(auth.get_db),
    user: models.User = Depends(auth.get_current_user)  # user'ı burada alıyoruz
):
    events = db.query(models.Event).filter(models.Event.approved == True).all()
    result = []
    for e in events:
        event_data = e.__dict__.copy()
        if not e.image:
            image_url = "/uploads/deneme.jpg"
        else:
            image_filename = os.path.basename(e.image)
            image_url = f"/uploads/{image_filename}"
        event_data['image'] = image_url
        event_data['owned_by_me'] = (e.owner_id == user.id)  # user.id artık mevcut
        result.append(event_data)
    return result

@router.post('/', response_model=schemas.EventOut)
def add_event(
    title: str = Form(...),
    description: str = Form(...),
    date: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(auth.get_db),
    user: models.User = Depends(get_user)
):
    filename = None
    if image:
        file_ext = os.path.splitext(image.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        filename = os.path.join(upload_dir, unique_name)
        with open(filename, "wb") as buffer:
            buffer.write(image.file.read())
    date_obj = datetime.fromisoformat(date)
    ev = models.Event(
        title=title,
        description=description,
        date=date_obj,
        location=location,
        image=filename,
        owner_id=user.id
    )
    db.add(ev); db.commit(); db.refresh(ev)
    event_data = ev.__dict__.copy()
    if not event_data.get('image'):
        image_url = "/uploads/deneme.jpg"
    else:
        image_filename = os.path.basename(event_data['image'])
        image_url = f"/uploads/{image_filename}"
    event_data['image'] = image_url
    event_data['owned_by_me'] = True
    return event_data

@router.delete('/{id}', status_code=204)
def remove_event(id: int, db: Session = Depends(auth.get_db), user: models.User = Depends(get_user)):
    ev = db.query(models.Event).get(id)
    if not ev or (ev.owner_id != user.id and user.role != "admin"):
        raise HTTPException(404)
    db.delete(ev); db.commit()

