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


async def validate_university_api_config(db: Session, university_id: int, endpoint_key: str) -> Dict[str, Any]:
    """Проверить и получить конфигурацию University API для конкретного университета
    
    Args:
        db: Сессия базы данных
        university_id: ID университета
        endpoint_key: Ключ endpoint для проверки (например, "students_login")
    
    Returns:
        Конфигурация University API с флагом use_ghost_api, если endpoint пустой
    
    Raises:
        HTTPException: Если конфигурация не найдена или endpoint выключен
    """
    config = await get_university_config(db, university_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"University API не настроен для университета {university_id}"
        )
    
    # Проверяем, указан ли endpoint в конфигурации
    endpoints = config.get("endpoints", {})
    
    # Если endpoint включен (есть в конфигурации), но пустой - используем ghost-api
    if endpoint_key in endpoints:
        endpoint_value = endpoints.get(endpoint_key, "").strip()
        if not endpoint_value:
            # Endpoint включен, но пустой - используем ghost-api
            config["use_ghost_api"] = True
            return config
    
    # Если endpoint не включен (нет в конфигурации) - возвращаем 404
    if endpoint_key not in endpoints:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Endpoint '{endpoint_key}' не настроен для университета {university_id}"
        )
    
    # Endpoint включен и имеет значение - используем University API
    config["use_ghost_api"] = False
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
    except httpx.HTTPStatusError as e:
        # Логируем детали ошибки для диагностики
        status_code = e.response.status_code
        if status_code == 401:
            error_detail = "Неверный email или пароль"
        elif status_code == 405:
            # HTTP 405 - Method Not Allowed, обычно означает неправильный URL или метод
            error_detail = f"Ошибка конфигурации University API: неправильный endpoint (HTTP 405). Проверьте конфигурацию endpoints в БД."
            logger.error(f"HTTP 405 при логине. URL: {e.request.url}, Method: {e.request.method}")
        elif status_code == 503:
            error_detail = "University API недоступен"
        elif status_code == 404:
            error_detail = f"Endpoint не найден (HTTP 404). Проверьте конфигурацию University API."
        else:
            error_detail = f"Ошибка University API: HTTP {status_code}"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
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
    
    # Если существует запись с таким user_id
    if existing_credential:
        # Если email тот же - просто обновляем
        if existing_credential.student_email == student_email:
            was_inactive = not existing_credential.is_active
            existing_credential.is_active = True
            db.commit()
            db.refresh(existing_credential)
            return existing_credential, was_inactive
        else:
            # Если email другой - удаляем старую запись и создаем новую
            credentials_repo.delete_by_user_id(user_id)
            db.commit()
            # Создаем новую запись
            credential = credentials_repo.create(
                user_id=user_id,
                student_email=student_email
            )
            db.commit()
            db.refresh(credential)
            return credential, False
    else:
        # Проверяем, нет ли записи с таким user_id (на случай, если existing_credential не был передан)
        existing = credentials_repo.get_by_user_id_any(user_id)
        if existing:
            # Удаляем старую запись
            credentials_repo.delete_by_user_id(user_id)
            db.commit()
        
        # Создаем новую запись
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
    
    Примечание:
        - Тестовый аккаунт test@test.ru может использоваться любым user_id
        - Если user_id уже существует, старая связь будет удалена при сохранении
    """
    # Тестовый аккаунт может использоваться любым user_id
    if student_email.lower() == "test@test.ru":
        return
    
    # Проверяем, не используется ли email другим user_id
    existing_email = credentials_repo.get_by_email(student_email)
    if existing_email and existing_email.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот email уже привязан к другому пользователю"
        )
    
    # Если user_id уже существует, это нормально - старая связь будет удалена при сохранении

