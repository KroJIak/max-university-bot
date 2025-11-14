from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from core.database import Base


class Dean(Base):
    """Модель для хранения контактов деканатов"""
    __tablename__ = "deans"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, nullable=False, index=True)
    faculty = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Department(Base):
    """Модель для хранения контактов кафедр"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, nullable=False, index=True)
    faculty = Column(String, nullable=False)
    department = Column(String, nullable=False)
    phones = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

