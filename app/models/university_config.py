from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from core.database import Base


class UniversityConfig(Base):
    """Конфигурация University API"""
    __tablename__ = "university_config"

    id = Column(Integer, primary_key=True, index=True)
    university_api_base_url = Column(String, nullable=False)
    endpoints = Column(JSON, nullable=False, default={})  # {"feature_id": "endpoint"}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

