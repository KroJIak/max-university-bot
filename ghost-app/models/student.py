from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from core.database import Base


class Student(Base):
    """Модель для хранения данных студентов"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, nullable=False, index=True)
    student_email = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    group = Column(String, nullable=True)
    course = Column(String, nullable=True)
    photo = Column(Text, nullable=True)  # base64 data URI
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

