from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from repositories.user_repository import UserRepository
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class UserCreate(BaseModel):
    user_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


class UserResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str | None
    username: str | None

    class Config:
        from_attributes = True


# CREATE
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Создать нового пользователя"""
    user_repo = UserRepository(db)
    
    if user_repo.exists(user.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    db_user = user_repo.create(
        user_id=user.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )
    return db_user


# READ - Get by user_id
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по user_id"""
    user_repo = UserRepository(db)
    db_user = user_repo.get_by_user_id(user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


# READ - Get all
@router.get("/users", response_model=list[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех пользователей"""
    user_repo = UserRepository(db)
    users = user_repo.get_all(skip=skip, limit=limit)
    return users


# UPDATE
@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Обновить данные пользователя"""
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
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удалить пользователя"""
    user_repo = UserRepository(db)
    
    if not user_repo.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None

