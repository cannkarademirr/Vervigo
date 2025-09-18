from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from .. import schemas, models, auth

router = APIRouter(prefix="/businesses", tags=["businesses"])

def get_user(u = Depends(auth.get_current_user)): return u

@router.get('/', response_model=List[schemas.BusinessOut])
def show_businesses(db: Session = Depends(auth.get_db)):
    return db.query(models.Business).filter(models.Business.approved == True).all()

@router.post('/', response_model=schemas.BusinessOut)
def add_business(data: schemas.BusinessCreate, db: Session = Depends(auth.get_db), user: models.User = Depends(get_user)):
    b = models.Business(**data.dict(), owner_id=user.id)
    db.add(b); db.commit(); db.refresh(b)
    return b

@router.delete("/{id}", status_code=204)
def remove_business(id: int, db: Session = Depends(auth.get_db), user: models.User = Depends(auth.get_current_user)):
    business = db.query(models.Business).get(id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this business")
    owner = db.query(models.User).get(business.owner_id)
    if owner and owner.role == "owner":
        owner.role = "customer"
    db.delete(business)
    db.commit()