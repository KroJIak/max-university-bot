"""Pydantic схемы для студентов"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime


class StudentLoginRequest(BaseModel):
    """Запрос на логин студента на сайте университета
    
    Выполняет логин на сайте университета с использованием credentials студента
    и сохраняет связь между пользователем MAX и аккаунтом студента.
    """
    user_id: int = Field(..., description="ID пользователя в системе MAX", example=123456789)
    university_id: int = Field(..., description="ID университета", example=1)
    student_email: EmailStr = Field(..., description="Email студента для входа на сайт университета", example="student@university.ru")
    password: str = Field(..., description="Пароль студента для входа на сайт университета", example="password123")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123456789,
                "university_id": 1,
                "student_email": "student@university.ru",
                "password": "password123"
            }
        }


class StudentLoginResponse(BaseModel):
    """Ответ на запрос логина студента
    
    Содержит результат попытки логина и информацию о связке пользователя с аккаунтом студента.
    """
    success: bool = Field(..., description="Успешность операции логина", example=True)
    message: str = Field(..., description="Сообщение о результате операции", example="Login successful")
    student_email: Optional[str] = Field(None, description="Email студента (если успешно)", example="student@university.ru")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Login successful",
                "student_email": "student@university.ru"
            }
        }


class StudentStatusResponse(BaseModel):
    """Статус связи пользователя с аккаунтом студента
    
    Показывает, связан ли пользователь с аккаунтом студента и когда была создана связь.
    """
    is_linked: bool = Field(..., description="Связан ли пользователь с аккаунтом студента", example=True)
    student_email: Optional[str] = Field(None, description="Email студента (если связан)", example="student@university.ru")
    linked_at: Optional[datetime] = Field(None, description="Дата и время создания связи", example="2024-01-15T10:30:00Z")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_linked": True,
                "student_email": "student@university.ru",
                "linked_at": "2024-01-15T10:30:00Z"
            }
        }


class StudentCredentialsResponse(BaseModel):
    """Ответ с данными credentials студента
    
    Содержит информацию о связи пользователя MAX с аккаунтом студента.
    """
    id: int = Field(..., description="ID записи credentials", example=1)
    user_id: int = Field(..., description="ID пользователя в системе MAX", example=123456789)
    student_email: str = Field(..., description="Email студента", example="student@university.ru")
    is_active: bool = Field(..., description="Активна ли связь", example=True)
    created_at: datetime = Field(..., description="Дата и время создания связи", example="2024-01-15T10:30:00Z")
    last_login_at: Optional[datetime] = Field(None, description="Дата и время последнего логина", example="2024-01-15T10:30:00Z")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123456789,
                "student_email": "student@university.ru",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "last_login_at": "2024-01-15T10:30:00Z"
            }
        }


class StudentCredentialsUpdate(BaseModel):
    """Обновление credentials студента
    
    Позволяет обновить email студента или выполнить повторный логин с новым паролем.
    """
    student_email: Optional[EmailStr] = Field(None, description="Новый email студента", example="newstudent@university.ru")
    password: Optional[str] = Field(None, description="Новый пароль для повторного логина", example="newpassword123")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_email": "newstudent@university.ru",
                "password": "newpassword123"
            }
        }


class TeachersResponse(BaseModel):
    """Ответ со списком преподавателей
    
    Содержит список всех преподавателей университета с их ID и ФИО.
    """
    success: bool = Field(..., description="Успешность операции", example=True)
    teachers: Optional[list] = Field(None, description="Список преподавателей: [{\"id\": \"tech0001\", \"name\": \"ФИО\"}, ...]", example=[{"id": "tech0001", "name": "Иванов Иван Иванович"}, {"id": "tech0002", "name": "Петров Петр Петрович"}])
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "teachers": [
                    {"id": "tech0001", "name": "Иванов Иван Иванович"},
                    {"id": "tech0002", "name": "Петров Петр Петрович"}
                ],
                "error": None
            }
        }


class PersonalDataResponse(BaseModel):
    """Ответ с данными студента
    
    Содержит структурированные данные студента с личного кабинета университета.
    """
    success: bool = Field(..., description="Успешность операции", example=True)
    data: Optional[Dict[str, Optional[str]]] = Field(None, description="Структурированные данные студента (ФИО, группа, курс, фото и т.д.)", example={"full_name": "Иванов Иван Иванович", "group": "ИВТ-21-01", "course": "3", "photo": "data:image/jpeg;base64,..."})
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "full_name": "Иванов Иван Иванович",
                    "group": "ИВТ-21-01",
                    "course": "3",
                    "photo": "data:image/jpeg;base64,..."
                },
                "error": None
            }
        }


class TeacherInfoResponse(BaseModel):
    """Ответ с информацией о преподавателе
    
    Содержит информацию о кафедрах преподавателя и его фото.
    """
    success: bool = Field(..., description="Успешность операции", example=True)
    departments: Optional[list] = Field(None, description="Список кафедр преподавателя", example=["Кафедра информатики", "Кафедра программирования"])
    photo: Optional[str] = Field(None, description="Фото преподавателя в формате base64 data URI", example="data:image/jpeg;base64,...")
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "departments": ["Кафедра информатики", "Кафедра программирования"],
                "photo": "data:image/jpeg;base64,...",
                "error": None
            }
        }


class ScheduleResponse(BaseModel):
    """Ответ с расписанием студента
    
    Содержит список занятий студента на текущую или следующую неделю.
    """
    success: bool = Field(..., description="Успешность операции", example=True)
    schedule: Optional[list] = Field(None, description="Список занятий: [{\"date\": \"2024-01-15\", \"time_start\": \"09:00\", \"time_end\": \"10:30\", \"subject\": \"Математика\", \"type\": \"Лекция\", \"teacher\": \"Иванов И.И.\", \"room\": \"101\"}, ...]", example=[{"date": "2024-01-15", "time_start": "09:00", "time_end": "10:30", "subject": "Математика", "type": "Лекция", "teacher": "Иванов И.И.", "room": "101"}])
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "schedule": [
                    {
                        "date": "2024-01-15",
                        "time_start": "09:00",
                        "time_end": "10:30",
                        "subject": "Математика",
                        "type": "Лекция",
                        "teacher": "Иванов И.И.",
                        "room": "101"
                    }
                ],
                "error": None
            }
        }


class ContactsResponse(BaseModel):
    """Ответ с контактами деканатов и кафедр
    
    Содержит контактную информацию деканатов факультетов и кафедр.
    """
    success: bool = Field(..., description="Успешность операции", example=True)
    deans: Optional[list] = Field(None, description="Список деканатов: [{\"faculty\": \"Факультет информатики\", \"phone\": \"+7 (123) 456-78-90\", \"email\": \"dean@university.ru\"}, ...]", example=[{"faculty": "Факультет информатики", "phone": "+7 (123) 456-78-90", "email": "dean@university.ru"}])
    departments: Optional[list] = Field(None, description="Список кафедр: [{\"faculty\": \"Факультет информатики\", \"department\": \"Кафедра программирования\", \"phones\": \"+7 (123) 456-78-90\", \"email\": \"dept@university.ru\"}, ...]", example=[{"faculty": "Факультет информатики", "department": "Кафедра программирования", "phones": "+7 (123) 456-78-90", "email": "dept@university.ru"}])
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "deans": [
                    {"faculty": "Факультет информатики", "phone": "+7 (123) 456-78-90", "email": "dean@university.ru"}
                ],
                "departments": [
                    {"faculty": "Факультет информатики", "department": "Кафедра программирования", "phones": "+7 (123) 456-78-90", "email": "dept@university.ru"}
                ],
                "error": None
            }
        }


class PlatformsResponse(BaseModel):
    """Ответ со списком полезных веб-платформ
    
    Содержит список полезных веб-платформ университета для студентов.
    """
    success: bool = Field(..., description="Успешность операции", example=True)
    platforms: Optional[list] = Field(None, description="Список платформ: [{\"key\": \"moodle\", \"name\": \"Moodle\", \"url\": \"https://moodle.university.ru\", \"emoji\": \"📚\"}, ...]", example=[{"key": "moodle", "name": "Moodle", "url": "https://moodle.university.ru", "emoji": "📚"}, {"key": "library", "name": "Электронная библиотека", "url": "https://library.university.ru", "emoji": "📖"}])
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "platforms": [
                    {"key": "moodle", "name": "Moodle", "url": "https://moodle.university.ru", "emoji": "📚"},
                    {"key": "library", "name": "Электронная библиотека", "url": "https://library.university.ru", "emoji": "📖"}
                ],
                "error": None
            }
        }


class MapsResponse(BaseModel):
    """Ответ со списком карт корпусов"""
    buildings: list = Field(..., description="Список корпусов с картами")
    
    class Config:
        json_schema_extra = {
            "example": {
                "buildings": [
                    {
                        "name": "Главный корпус",
                        "latitude": 56.123456,
                        "longitude": 47.123456,
                        "yandex_map_url": "https://yandex.ru/maps/?pt=47.123456,56.123456&z=17",
                        "gis2_map_url": "https://2gis.ru/cheboksary/firm/70000001012345678",
                        "google_map_url": "https://www.google.com/maps?q=56.123456,47.123456"
                    }
                ]
            }
        }


class ServicesResponse(BaseModel):
    """Ответ со списком сервисов
    
    Содержит список сервисов университета для студентов (не веб-платформы).
    """
    success: bool = Field(..., description="Успешность операции", example=True)
    services: Optional[list] = Field(None, description="Список сервисов: [{\"key\": \"schedule\", \"name\": \"Расписание\", \"emoji\": \"📅\"}, ...]", example=[{"key": "schedule", "name": "Расписание", "emoji": "📅"}, {"key": "teachers", "name": "Преподаватели", "emoji": "👨‍🏫"}])
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "services": [
                    {"key": "schedule", "name": "Расписание", "emoji": "📅"},
                    {"key": "teachers", "name": "Преподаватели", "emoji": "👨‍🏫"},
                    {"key": "map", "name": "Карта", "emoji": "🗺️"},
                    {"key": "contacts", "name": "Контакты", "emoji": "📞"},
                    {"key": "chats", "name": "Чаты", "emoji": "💬"}
                ],
                "error": None
            }
        }

