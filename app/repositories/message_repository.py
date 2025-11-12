from sqlalchemy.orm import Session
from models.messages import Message
from typing import Optional


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, message_id: int, user_id: int, text: Optional[str] = None, chat_id: Optional[int] = None) -> Message:
        db_message = Message(
            message_id=message_id,
            user_id=user_id,
            text=text,
            chat_id=chat_id
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_by_message_id(self, message_id: int) -> Optional[Message]:
        return self.db.query(Message).filter(Message.message_id == message_id).first()

    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Message]:
        return self.db.query(Message).filter(Message.user_id == user_id).offset(skip).limit(limit).all()

    def get_by_chat_id(self, chat_id: int, skip: int = 0, limit: int = 100) -> list[Message]:
        return self.db.query(Message).filter(Message.chat_id == chat_id).offset(skip).limit(limit).all()

