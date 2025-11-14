from sqlalchemy.orm import Session
from models.platform import Platform
from typing import List, Optional


class PlatformRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_university(self, university_id: int) -> List[Platform]:
        """Получить все платформы университета"""
        return self.db.query(Platform).filter(
            Platform.university_id == university_id
        ).all()

    def get_by_key(self, university_id: int, key: str) -> Optional[Platform]:
        """Получить платформу по ключу"""
        return self.db.query(Platform).filter(
            Platform.university_id == university_id,
            Platform.key == key
        ).first()

    def create_or_update(self, university_id: int, key: str, **kwargs) -> Platform:
        """Создать или обновить платформу"""
        platform = self.get_by_key(university_id, key)
        if platform:
            for k, v in kwargs.items():
                if hasattr(platform, k) and v is not None:
                    setattr(platform, k, v)
        else:
            platform = Platform(
                university_id=university_id,
                key=key,
                **kwargs
            )
            self.db.add(platform)
        self.db.commit()
        self.db.refresh(platform)
        return platform

