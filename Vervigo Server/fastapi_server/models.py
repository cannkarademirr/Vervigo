
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime
from sqlalchemy import Float

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default='customer')
    location = Column(String, default='')

    events = relationship("Event", back_populates="owner")
    businesses = relationship("Business", back_populates="owner")

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    location = Column(String)
    approved = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    image = Column(String, nullable=True) 
    owner = relationship("User", back_populates="events")


class Business(Base):
    __tablename__ = 'businesses'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    approved = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="businesses")
    
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String, default="completed")
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    qrcode_path = Column(String, nullable=True)
    used = Column(Boolean, default=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=True)  # 👈 Event ID eklendi
    event = relationship("Event")
    user = relationship("User")
    qrcode_hash = Column(String, nullable=True)  # 👈 QR kod için eşsiz hash