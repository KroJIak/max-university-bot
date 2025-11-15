from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from repositories.user_repository import UserRepository
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()


class UserCreate(BaseModel):
    """Запрос на создание пользователя
    
    Создает нового пользователя в системе MAX с привязкой к университету.
    """
    user_id: int = Field(..., description="ID пользователя в системе MAX", example=123456789)
    university_id: int = Field(..., description="ID университета, к которому привязан пользователь", example=1)
    first_name: str = Field(..., description="Имя пользователя", example="Иван")
    last_name: str | None = Field(None, description="Фамилия пользователя", example="Иванов")
    username: str | None = Field(None, description="Username пользователя в MAX", example="ivan_ivanov")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123456789,
                "university_id": 1,
                "first_name": "Иван",
                "last_name": "Иванов",
                "username": "ivan_ivanov"
            }
        }


class UserUpdate(BaseModel):
    """Запрос на обновление данных пользователя
    
    Позволяет обновить имя, фамилию или username пользователя.
    """
    first_name: str | None = Field(None, description="Новое имя пользователя", example="Петр")
    last_name: str | None = Field(None, description="Новая фамилия пользователя", example="Петров")
    username: str | None = Field(None, description="Новый username пользователя", example="petr_petrov")
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Петр",
                "last_name": "Петров",
                "username": "petr_petrov"
            }
        }


class UserResponse(BaseModel):
    """Ответ с данными пользователя
    
    Содержит полную информацию о пользователе системы MAX.
    """
    id: int = Field(..., description="Внутренний ID пользователя в БД", example=1)
    user_id: int = Field(..., description="ID пользователя в системе MAX", example=123456789)
    university_id: int = Field(..., description="ID университета, к которому привязан пользователь", example=1)
    first_name: str = Field(..., description="Имя пользователя", example="Иван")
    last_name: str | None = Field(None, description="Фамилия пользователя", example="Иванов")
    username: str | None = Field(None, description="Username пользователя в MAX", example="ivan_ivanov")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123456789,
                "university_id": 1,
                "first_name": "Иван",
                "last_name": "Иванов",
                "username": "ivan_ivanov"
            }
        }


# CREATE
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    description="Создает нового пользователя в системе MAX с привязкой к университету. Пользователь должен существовать в MAX и иметь уникальный user_id.",
    response_description="Созданный пользователь с полной информацией",
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {"description": "Пользователь уже существует"},
        404: {"description": "Университет не найден"}
    }
)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Создать нового пользователя
    
    Создает нового пользователя в системе MAX с привязкой к указанному университету.
    Пользователь должен существовать в MAX и иметь уникальный user_id.
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8003/api/v1/users",
        json={
            "user_id": 123456789,
            "university_id": 1,
            "first_name": "Иван",
            "last_name": "Иванов",
            "username": "ivan_ivanov"
        }
    )
    ```
    """
    from repositories.university_repository import UniversityRepository
    
    user_repo = UserRepository(db)
    university_repo = UniversityRepository(db)
    
    # Проверяем, существует ли университет
    university = university_repo.get_by_id(user.university_id)
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Университет с ID {user.university_id} не найден"
        )
    
    if user_repo.exists(user.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    db_user = user_repo.create(
        user_id=user.user_id,
        university_id=user.university_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )
    return db_user


# READ - Get by user_id
@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя",
    description="Получает информацию о пользователе по его user_id.",
    response_description="Информация о пользователе",
    responses={
        200: {"description": "Пользователь найден"},
        404: {"description": "Пользователь не найден"}
    }
)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по user_id
    
    Возвращает полную информацию о пользователе по его user_id.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/users/123456789")
    ```
    """
    user_repo = UserRepository(db)
    db_user = user_repo.get_by_user_id(user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


# READ - Get all
@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Получить список пользователей",
    description="Получает список всех пользователей системы с пагинацией.",
    response_description="Список пользователей",
    responses={
        200: {"description": "Список пользователей успешно получен"}
    }
)
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех пользователей
    
    Возвращает список всех пользователей системы с поддержкой пагинации.
    
    **Параметры:**
    - `skip`: Количество пропускаемых записей (по умолчанию: 0)
    - `limit`: Максимальное количество записей (по умолчанию: 100)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Получить первые 10 пользователей
    response = requests.get("http://localhost:8003/api/v1/users?skip=0&limit=10")
    
    # Получить следующие 10 пользователей
    response = requests.get("http://localhost:8003/api/v1/users?skip=10&limit=10")
    ```
    """
    user_repo = UserRepository(db)
    users = user_repo.get_all(skip=skip, limit=limit)
    return users


# UPDATE
@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Обновить пользователя",
    description="Обновляет данные пользователя (имя, фамилия, username). Можно обновить только указанные поля.",
    response_description="Обновленный пользователь",
    responses={
        200: {"description": "Пользователь успешно обновлен"},
        404: {"description": "Пользователь не найден"}
    }
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Обновить данные пользователя
    
    Обновляет данные пользователя. Можно обновить только указанные поля.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX
    - `user_update`: Данные для обновления (все поля опциональны)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Обновить имя и фамилию
    response = requests.put(
        "http://localhost:8003/api/v1/users/123456789",
        json={
            "first_name": "Петр",
            "last_name": "Петров"
        }
    )
    ```
    """
    user_repo = UserRepository(db)
    
    db_user = user_repo.update(
        user_id=user_id,
        first_name=user_update.first_name,
        last_name=user_update.last_name,
        username=user_update.username
    )
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return db_user


# DELETE
@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    description="Удаляет пользователя из системы. Внимание: это действие необратимо!",
    response_description="Пользователь успешно удален",
    responses={
        204: {"description": "Пользователь успешно удален"},
        404: {"description": "Пользователь не найден"}
    }
)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удалить пользователя
    
    Удаляет пользователя из системы. Это действие необратимо!
    Также удаляются все связанные данные (credentials студентов и т.д.).
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.delete("http://localhost:8003/api/v1/users/123456789")
    ```
    """
    user_repo = UserRepository(db)
    
    if not user_repo.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None

