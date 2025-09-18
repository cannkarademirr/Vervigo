from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/register', response_model=schemas.UserOut)
def register(data: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    user = models.User(name=data.name, email=data.email,
                    hashed_password=auth.get_password_hash(data.password),
                    location=data.location or "")
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post('/login', response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Incorrect email or password")
    token = auth.create_access_token({
        "sub": str(user.id),
        "role": user.role
        })
    return {"access_token": token, "token_type": "bearer"}

@router.get('/me', response_model=schemas.UserOut)
def get_current_user_info(user: models.User = Depends(auth.get_current_user)):
    return user