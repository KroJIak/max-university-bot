"""Pydantic схемы для студентов"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime


class StudentLoginRequest(BaseModel):
    """Запрос на логин студента"""
    user_id: int
    student_email: EmailStr
    password: str


class StudentLoginResponse(BaseModel):
    """Ответ на запрос логина"""
    success: bool
    message: str
    student_email: Optional[str] = None


class StudentStatusResponse(BaseModel):
    """Статус связи пользователя с аккаунтом студента"""
    is_linked: bool
    student_email: Optional[str] = None
    linked_at: Optional[datetime] = None


class StudentCredentialsResponse(BaseModel):
    """Ответ с данными credentials"""
    id: int
    user_id: int
    student_email: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentCredentialsUpdate(BaseModel):
    """Обновление credentials"""
    student_email: Optional[EmailStr] = None
    password: Optional[str] = None


class TeachersResponse(BaseModel):
    """Ответ со списком преподавателей"""
    success: bool
    teachers: Optional[list] = None  # Список преподавателей: [{"id": "tech0001", "name": "ФИО"}, ...]
    error: Optional[str] = None


class PersonalDataResponse(BaseModel):
    """Ответ с данными студента"""
    success: bool
    data: Optional[Dict[str, Optional[str]]] = None  # Структурированные данные студента
    error: Optional[str] = None


class TeacherInfoResponse(BaseModel):
    """Ответ с информацией о преподавателе"""
    success: bool
    departments: Optional[list] = None  # Список кафедр
    photo: Optional[str] = None  # Фото в формате base64 data URI
    error: Optional[str] = None


class ScheduleResponse(BaseModel):
    """Ответ с расписанием"""
    success: bool
    schedule: Optional[list] = None  # Список занятий
    error: Optional[str] = None


class ContactsResponse(BaseModel):
    """Ответ с контактами деканатов и кафедр"""
    success: bool
    deans: Optional[list] = None  # Список деканатов
    departments: Optional[list] = None  # Список кафедр
    error: Optional[str] = None


class PlatformsResponse(BaseModel):
    """Ответ со списком полезных веб-платформ"""
    success: bool
    platforms: Optional[list] = None  # Список платформ: [{"key": "...", "name": "...", "url": "..."}, ...]
    error: Optional[str] = None

