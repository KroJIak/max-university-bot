from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from core.database import Base


class Teacher(Base):
    """Модель для хранения данных преподавателей"""
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, nullable=False, index=True)
    teacher_id = Column(String, nullable=False, index=True)  # ID преподавателя (например, "2173")
    name = Column(String, nullable=False)
    departments = Column(String, nullable=True)  # JSON массив кафедр
    photo = Column(Text, nullable=True)  # base64 data URI
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

