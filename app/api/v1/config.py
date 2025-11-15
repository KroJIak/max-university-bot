from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_current_university_id
from repositories.university_config_repository import UniversityConfigRepository
from repositories.university_repository import UniversityRepository
from pydantic import BaseModel, Field
from typing import Dict, Optional

router = APIRouter()


class UniversityConfigRequest(BaseModel):
    """Запрос на создание/обновление конфигурации University API
    
    Позволяет настроить базовый URL University API и endpoints для различных функций.
    """
    university_id: int = Field(..., description="ID университета", example=1)
    university_api_base_url: str = Field(..., description="Базовый URL University API", example="http://university-api:8002")
    endpoints: Dict[str, str] = Field(default_factory=dict, description="Словарь endpoints: {\"students_login\": \"/students/login\", \"students_personal_data\": \"/students/personal_data\", ...}", example={"students_login": "/students/login", "students_personal_data": "/students/personal_data", "students_teachers": "/students/teachers"})
    
    class Config:
        json_schema_extra = {
            "example": {
                "university_id": 1,
                "university_api_base_url": "http://university-api:8002",
                "endpoints": {
                    "students_login": "/students/login",
                    "students_personal_data": "/students/personal_data",
                    "students_teachers": "/students/teachers",
                    "students_schedule": "/students/schedule",
                    "students_contacts": "/students/contacts",
                    "students_platforms": "/students/platforms",
                    "students_maps": "/students/maps",
                    "students_teacher_info": "/students/teacher_info"
                }
            }
        }


class UniversityConfigResponse(BaseModel):
    """Ответ с конфигурацией University API
    
    Содержит полную конфигурацию University API для университета.
    """
    id: int = Field(..., description="ID конфигурации", example=1)
    university_id: int = Field(..., description="ID университета", example=1)
    university_api_base_url: str = Field(..., description="Базовый URL University API", example="http://university-api:8002")
    endpoints: Dict[str, str] = Field(..., description="Словарь endpoints", example={"students_login": "/students/login", "students_personal_data": "/students/personal_data"})

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "university_id": 1,
                "university_api_base_url": "http://university-api:8002",
                "endpoints": {
                    "students_login": "/students/login",
                    "students_personal_data": "/students/personal_data",
                    "students_teachers": "/students/teachers",
                    "students_schedule": "/students/schedule",
                    "students_contacts": "/students/contacts",
                    "students_platforms": "/students/platforms",
                    "students_maps": "/students/maps",
                    "students_teacher_info": "/students/teacher_info"
                }
            }
        }


@router.get(
    "/config/university/{university_id}",
    response_model=UniversityConfigResponse,
    summary="Получить конфигурацию университета",
    description="Получает конфигурацию University API для указанного университета. Не требует аутентификации.",
    response_description="Конфигурация University API",
    responses={
        200: {"description": "Конфигурация успешно получена"},
        404: {"description": "Конфигурация не найдена"}
    }
)
async def get_university_config(
    university_id: int, 
    db: Session = Depends(get_db)
):
    """Получить конфигурацию University API для конкретного университета
    
    Получает конфигурацию University API для указанного университета.
    Не требует аутентификации.
    
    **Параметры:**
    - `university_id`: ID университета
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Получаем конфигурацию
    response = requests.get(
        "http://localhost:8003/api/v1/config/university/1"
    )
    ```
    """
    repo = UniversityConfigRepository(db)
    config = repo.get(university_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Конфигурация для университета {university_id} не найдена"
        )
    
    return config


@router.put(
    "/config/university",
    response_model=UniversityConfigResponse,
    summary="Обновить конфигурацию университета",
    description="Создает или обновляет конфигурацию University API для указанного университета. Требуется аутентификация через JWT токен. Можно обновить только свою конфигурацию.",
    response_description="Обновленная конфигурация University API",
    responses={
        200: {"description": "Конфигурация успешно обновлена"},
        401: {"description": "Требуется аутентификация"},
        403: {"description": "Доступ запрещен (можно обновить только свою конфигурацию)"},
        404: {"description": "Университет не найден"},
        500: {"description": "Ошибка сохранения конфигурации"}
    }
)
async def update_university_config(
    request: UniversityConfigRequest,
    db: Session = Depends(get_db),
    current_university_id: int = Depends(get_current_university_id)
):
    """Создать или обновить конфигурацию University API
    
    Создает или обновляет конфигурацию University API для указанного университета.
    Требуется аутентификация через JWT токен (полученный через `/universities/login`).
    Можно обновить только свою конфигурацию.
    
    **Заголовки:**
    - `Authorization: Bearer <token>` - JWT токен университета
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Сначала аутентифицируемся
    login_response = requests.post(
        "http://localhost:8003/api/v1/universities/login",
        json={
            "university_id": 1,
            "login": "admin",
            "password": "admin"
        }
    )
    token = login_response.json()["access_token"]
    
    # Обновляем конфигурацию
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        "http://localhost:8003/api/v1/config/university",
        headers=headers,
        json={
            "university_id": 1,
            "university_api_base_url": "http://university-api:8002",
            "endpoints": {
                "students_login": "/students/login",
                "students_personal_data": "/students/personal_data",
                "students_teachers": "/students/teachers"
            }
        }
    )
    ```
    """
    # Проверяем, что пользователь аутентифицирован для этого университета
    if current_university_id != request.university_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен: вы не можете изменить конфигурацию другого университета"
        )
    
    university_repo = UniversityRepository(db)
    config_repo = UniversityConfigRepository(db)
    
    # Проверяем, существует ли университет
    university = university_repo.get_by_id(request.university_id)
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Университет с ID {request.university_id} не найден"
        )
    
    try:
        config = config_repo.upsert(
            university_id=request.university_id,
            university_api_base_url=request.university_api_base_url,
            endpoints=request.endpoints
        )
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сохранения конфигурации: {str(e)}"
        )


@router.get(
    "/config/university/{university_id}/endpoints",
    response_model=Dict[str, str],
    summary="Получить endpoints университета",
    description="Получает только endpoints из конфигурации University API для указанного университета. Не требует аутентификации.",
    response_description="Словарь endpoints: {\"students_login\": \"/students/login\", ...}",
    responses={
        200: {"description": "Endpoints успешно получены"},
        404: {"description": "Конфигурация не найдена"}
    }
)
async def get_university_endpoints(
    university_id: int, 
    db: Session = Depends(get_db)
):
    """Получить только endpoints из конфигурации
    
    Получает только endpoints из конфигурации University API для указанного университета.
    Не требует аутентификации.
    
    **Параметры:**
    - `university_id`: ID университета
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Получаем endpoints
    response = requests.get(
        "http://localhost:8003/api/v1/config/university/1/endpoints"
    )
    ```
    """
    repo = UniversityConfigRepository(db)
    config = repo.get(university_id)
    
    if not config:
        return {}
    
    return config.endpoints


@router.get(
    "/config/university/{university_id}/endpoints/status",
    response_model=Dict[str, bool],
    summary="Получить статус endpoints университета",
    description="Получает статус endpoints (включен/выключен) для указанного университета. Не требует аутентификации.",
    response_description="Словарь со статусом endpoints: {\"students_login\": true, \"students_personal_data\": false, ...}",
    responses={
        200: {"description": "Статус endpoints успешно получен"},
        404: {"description": "Университет не найден"}
    }
)
async def get_university_endpoints_status(
    university_id: int, 
    db: Session = Depends(get_db)
):
    """Получить статус endpoints (включен/выключен)
    
    Получает статус endpoints (включен/выключен) для указанного университета.
    Не требует аутентификации.
    
    **Параметры:**
    - `university_id`: ID университета
    
    **Возвращает:**
    - `Dict[str, bool]`: Словарь с ключами endpoint и значениями true/false
      - `true`: endpoint включен (присутствует в конфигурации)
      - `false`: endpoint выключен (отсутствует в конфигурации)
    
    **Пример ответа:**
    ```json
    {
        "students_login": true,
        "students_personal_data": false,
        "students_teachers": true,
        "students_schedule": false,
        "students_contacts": false,
        "students_platforms": false,
        "students_maps": false,
        "students_teacher_info": false
    }
    ```
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Получаем статус endpoints
    response = requests.get(
        "http://localhost:8003/api/v1/config/university/1/endpoints/status"
    )
    ```
    """
    university_repo = UniversityRepository(db)
    config_repo = UniversityConfigRepository(db)
    
    # Проверяем, существует ли университет
    university = university_repo.get_by_id(university_id)
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Университет с ID {university_id} не найден"
        )
    
    # Получаем конфигурацию
    config = config_repo.get(university_id)
    
    # Список всех возможных endpoints
    all_endpoints = [
        "students_login",
        "students_personal_data",
        "students_teachers",
        "students_schedule",
        "students_contacts",
        "students_platforms",
        "students_maps",
        "students_teacher_info"
    ]
    
    # Если конфигурации нет, все endpoints выключены
    if not config:
        return {endpoint: False for endpoint in all_endpoints}
    
    # Проверяем каждый endpoint: если он есть в конфигурации, то включен (true)
    endpoints_status = {}
    for endpoint in all_endpoints:
        # Endpoint включен, если он присутствует в словаре endpoints конфигурации
        endpoints_status[endpoint] = endpoint in config.endpoints
    
    return endpoints_status

