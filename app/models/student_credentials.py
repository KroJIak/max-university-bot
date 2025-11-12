from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class StudentCredentials(Base):
    """Модель для связи пользователя MAX с email студента
    
    Cookies и пароли хранятся в university-app, здесь только связь user_id <-> student_email
    """
    __tablename__ = "student_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), unique=True, index=True, nullable=False)
    student_email = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

