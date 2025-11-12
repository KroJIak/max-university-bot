from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(BigInteger, unique=True, index=True, nullable=False)
    user_id = Column(BigInteger, index=True, nullable=False)
    chat_id = Column(BigInteger, index=True, nullable=True)
    text = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

