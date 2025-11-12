from sqlalchemy.orm import Session
from models.university_config import UniversityConfig
from typing import Optional, Dict


class UniversityConfigRepository:
    """Репозиторий для работы с конфигурацией University API"""

    def get(self, db: Session) -> Optional[UniversityConfig]:
        """Получить конфигурацию (должна быть только одна)"""
        return db.query(UniversityConfig).first()

    def create(self, db: Session, university_api_base_url: str, endpoints: Dict[str, str]) -> UniversityConfig:
        """Создать конфигурацию"""
        config = UniversityConfig(
            university_api_base_url=university_api_base_url,
            endpoints=endpoints
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    def update(self, db: Session, university_api_base_url: str, endpoints: Dict[str, str]) -> Optional[UniversityConfig]:
        """Обновить конфигурацию"""
        config = self.get(db)
        if config:
            config.university_api_base_url = university_api_base_url
            config.endpoints = endpoints
            db.commit()
            db.refresh(config)
            return config
        return None

    def upsert(self, db: Session, university_api_base_url: str, endpoints: Dict[str, str]) -> UniversityConfig:
        """Создать или обновить конфигурацию"""
        config = self.get(db)
        if config:
            return self.update(db, university_api_base_url, endpoints)
        else:
            return self.create(db, university_api_base_url, endpoints)

