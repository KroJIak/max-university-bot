from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Schedule(Base):
    """Модель для хранения расписания студентов"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, nullable=False, index=True)
    student_email = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    subject = Column(String, nullable=False)
    type = Column(String, nullable=True)  # Лекция, Практика, Лабораторная и т.д.
    teacher = Column(String, nullable=True)
    room = Column(String, nullable=True)
    week = Column(Integer, nullable=False, default=1)  # 1 = текущая неделя, 2 = следующая
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

