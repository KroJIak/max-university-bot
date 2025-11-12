from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from repositories.university_config_repository import UniversityConfigRepository
from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional

router = APIRouter()


class UniversityConfigRequest(BaseModel):
    """Запрос на создание/обновление конфигурации"""
    university_api_base_url: str
    endpoints: Dict[str, str] = {}


class UniversityConfigResponse(BaseModel):
    """Ответ с конфигурацией"""
    id: int
    university_api_base_url: str
    endpoints: Dict[str, str]

    class Config:
        from_attributes = True


@router.get("/config/university", response_model=UniversityConfigResponse)
async def get_university_config(db: Session = Depends(get_db)):
    """Получить конфигурацию University API"""
    repo = UniversityConfigRepository()
    config = repo.get(db)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Конфигурация не найдена"
        )
    
    return config


@router.put("/config/university", response_model=UniversityConfigResponse)
async def update_university_config(
    request: UniversityConfigRequest,
    db: Session = Depends(get_db)
):
    """Создать или обновить конфигурацию University API"""
    repo = UniversityConfigRepository()
    
    try:
        config = repo.upsert(
            db,
            university_api_base_url=request.university_api_base_url,
            endpoints=request.endpoints
        )
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сохранения конфигурации: {str(e)}"
        )


@router.get("/config/university/endpoints", response_model=Dict[str, str])
async def get_university_endpoints(db: Session = Depends(get_db)):
    """Получить только endpoints из конфигурации"""
    repo = UniversityConfigRepository()
    config = repo.get(db)
    
    if not config:
        return {}
    
    return config.endpoints

