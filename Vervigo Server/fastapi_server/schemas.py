from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from typing import Literal


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    location: Optional[str]

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    location: Optional[str]
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    location: str

class EventCreate(EventBase):
    image: Optional[str] = None 

class EventOut(EventBase):
    id: int
    approved: bool
    owner_id: int
    owned_by_me: bool  # Yeni alan eklendi
    image: Optional[str] = None  # Yeni alan
    class Config: orm_mode = True

class BusinessBase(BaseModel):
    name: str
    category: str

class BusinessCreate(BusinessBase): pass
class BusinessOut(BusinessBase):
    id: int
    approved: bool
    owner_id: int
    class Config: orm_mode = True

class ApproveItem(BaseModel):
    type: Literal["event", "business"]
    id: int
class PaymentCreate(BaseModel):
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    event_id: int  # 👈 Event ID eklendi

class PaymentOut(PaymentCreate):
    id: int
    status: str
    created_at: datetime
    qrcode_path: Optional[str] = None
    used: bool
    event_id: int
    qrcode_hash: Optional[str] = None  # 👈 QR kod hash’i eklendi
    class Config:
        orm_mode = True