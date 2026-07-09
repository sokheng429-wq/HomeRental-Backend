from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth / Users ----------


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    province: Optional[str] = None
    area: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    area: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Listings ----------


class ListingCreate(BaseModel):
    type: str
    title: Optional[str] = None
    location: str
    floor: Optional[int] = None
    rent: float
    description: Optional[str] = None
    owner_phone: Optional[str] = None
    tint: Optional[str] = "#5b6bd6"


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    title: str
    location: str
    floor: Optional[int] = None
    rent: float
    description: Optional[str] = None
    owner_phone: Optional[str] = None
    tint: Optional[str] = None
    created_at: datetime


# ---------- Chat ----------


class ChatMessageIn(BaseModel):
    text: str


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    text: str
    listing_id: Optional[int] = None
    created_at: datetime


class ChatReply(BaseModel):
    user_message: ChatMessageOut
    bot_message: ChatMessageOut
