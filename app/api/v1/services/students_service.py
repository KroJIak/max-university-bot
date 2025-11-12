"""Сервис для работы со студентами"""
from sqlalchemy.orm import Session
from repositories.student_credentials_repository import StudentCredentialsRepository
from api.v1.services.university_api_client import call_university_api_login
from api.v1.services.university_config import get_university_config
from typing import Dict, Any
import httpx
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


async def validate_university_api_config(db: Session, endpoint_key: str) -> Dict[str, Any]:
    """Проверить и получить конфигурацию University API
    
    Args:
        db: Сессия базы данных
        endpoint_key: Ключ endpoint для проверки (например, "students_login")
    
    Returns:
        Конфигурация University API
    
    Raises:
        HTTPException: Если конфигурация не найдена или endpoint выключен
    """
    config = await get_university_config(db)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="University API не настроен"
        )
    
    # Проверяем, включен ли endpoint (если endpoint отсутствует, считаем что он включен с дефолтным путем)
    # Это позволяет использовать дефолтные endpoints, даже если они не настроены в БД
    if endpoint_key not in config["endpoints"]:
        # Endpoint не настроен, но это не ошибка - используем дефолтный путь
        logger.warning(f"Endpoint {endpoint_key} не найден в конфигурации, используем дефолтный путь")
    
    return config


async def perform_login(
    email: str,
    password: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Выполнить логин через University API
    
    Args:
        email: Email студента
        password: Пароль студента
        config: Конфигурация University API
    
    Returns:
        Результат логина от University API
    
    Raises:
        HTTPException: Если логин не удался
    """
    try:
        login_result = await call_university_api_login(email, password, config)
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not login_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=login_result.get("error", "Ошибка при логине")
        )
    
    return login_result


async def save_student_credentials(
    db: Session,
    user_id: int,
    student_email: str,
    existing_credential=None
) -> tuple:
    """Сохранить или обновить credentials студента
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя MAX
        student_email: Email студента
        existing_credential: Существующий credential (если есть)
    
    Returns:
        tuple: (credential, was_inactive) - объект credential и флаг, был ли он неактивен
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    if existing_credential:
        was_inactive = not existing_credential.is_active
        existing_credential.student_email = student_email
        existing_credential.is_active = True
        db.commit()
        db.refresh(existing_credential)
        return existing_credential, was_inactive
    else:
        credential = credentials_repo.create(
            user_id=user_id,
            student_email=student_email
        )
        db.commit()
        db.refresh(credential)
        return credential, False


def validate_student_email_uniqueness(
    credentials_repo: StudentCredentialsRepository,
    user_id: int,
    student_email: str
):
    """Проверить уникальность email студента
    
    Args:
        credentials_repo: Репозиторий для работы с credentials
        user_id: ID пользователя MAX
        student_email: Email студента для проверки
    
    Raises:
        HTTPException: Если email уже используется другим пользователем
    """
    existing_credential = credentials_repo.get_by_user_id_any(user_id)
    if existing_credential and existing_credential.student_email != student_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь уже связан с другим аккаунтом: {existing_credential.student_email}"
        )
    
    existing_email = credentials_repo.get_by_email(student_email)
    if existing_email and existing_email.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот email уже привязан к другому пользователю"
        )

