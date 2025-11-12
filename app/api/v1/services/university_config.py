"""Сервис для работы с конфигурацией University API"""
from sqlalchemy.orm import Session
from repositories.university_config_repository import UniversityConfigRepository
from typing import Optional, Dict, Any


async def get_university_config(db: Session) -> Optional[Dict[str, Any]]:
    """Получить конфигурацию University API из БД
    
    Args:
        db: Сессия базы данных
    
    Returns:
        dict с ключами base_url и endpoints, или None если конфигурация не найдена
    """
    repo = UniversityConfigRepository()
    config = repo.get(db)
    
    if not config:
        return None
    
    return {
        "base_url": config.university_api_base_url,
        "endpoints": config.endpoints
    }

