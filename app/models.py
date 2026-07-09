from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(40), nullable=True)
    province = Column(String(80), nullable=True)
    area = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("Listing", back_populates="owner")
    messages = relationship("ChatMessage", back_populates="user")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    type = Column(String(40), nullable=False)  # Apartment / Condo / Studio
    title = Column(String(160), nullable=False)
    location = Column(String(120), nullable=False)
    floor = Column(Integer, nullable=True)
    rent = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    owner_phone = Column(String(40), nullable=True)
    tint = Column(String(20), default="#5b6bd6")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="listings")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(10), nullable=False)  # "user" or "bot"
    text = Column(Text, nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")
