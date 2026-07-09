from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user
from ..chatbot import generate_reply

router = APIRouter(prefix="/chat", tags=["chat"])

WELCOME_TEXT = "Hi! I'm here to help you find a room, apartment, or condo in Phnom Penh. Tell me a neighborhood and your budget."


@router.get("/history", response_model=list[schemas.ChatMessageOut])
def history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.user_id == current_user.id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )

    if not messages:
        welcome = models.ChatMessage(
            user_id=current_user.id, role="bot", text=WELCOME_TEXT
        )
        db.add(welcome)
        db.commit()
        db.refresh(welcome)
        messages = [welcome]

    return messages


@router.post("/message", response_model=schemas.ChatReply)
def send_message(
    payload: schemas.ChatMessageIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_msg = models.ChatMessage(
        user_id=current_user.id, role="user", text=payload.text
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    reply_text, listing_id = generate_reply(db, current_user.id, payload.text)

    bot_msg = models.ChatMessage(
        user_id=current_user.id,
        role="bot",
        text=reply_text,
        listing_id=listing_id,
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    return schemas.ChatReply(user_message=user_msg, bot_message=bot_msg)
