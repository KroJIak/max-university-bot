from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from core.database import Base


class SessionCookies(Base):
    """Модель для хранения cookies сессий по email студента"""
    __tablename__ = "session_cookies"

    id = Column(Integer, primary_key=True, index=True)
    student_email = Column(String, nullable=False, unique=True, index=True)
    # Cookies по доменам в JSON формате: {"tt.chuvsu.ru": "...", "lk.chuvsu.ru": "..."}
    cookies_by_domain = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

