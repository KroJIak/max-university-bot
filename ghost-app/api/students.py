"""API эндпоинты для студентов (симуляция university-app)"""
from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from core.database import get_db
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List
import json
from repositories.student_repository import StudentRepository
from repositories.schedule_repository import ScheduleRepository
from repositories.teacher_repository import TeacherRepository
from repositories.contact_repository import ContactRepository
from repositories.platform_repository import PlatformRepository
from datetime import date, time

router = APIRouter()


class LoginRequest(BaseModel):
    """Запрос на логин студента"""
    student_email: EmailStr = Field(..., description="Email студента")
    password: str = Field(..., description="Пароль студента")


class LoginResponse(BaseModel):
    """Ответ на запрос логина"""
    success: bool
    error: Optional[str] = None


class TeachersRequest(BaseModel):
    """Запрос на получение списка преподавателей"""
    student_email: EmailStr


class TeachersResponse(BaseModel):
    """Ответ со списком преподавателей"""
    success: bool
    teachers: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None


class PersonalDataRequest(BaseModel):
    """Запрос на получение данных студента"""
    student_email: EmailStr


class PersonalDataResponse(BaseModel):
    """Ответ с данными студента"""
    success: bool
    data: Optional[Dict[str, Optional[str]]] = None
    error: Optional[str] = None


class TeacherInfoRequest(BaseModel):
    """Запрос на получение информации о преподавателе"""
    student_email: EmailStr
    teacher_id: str


class TeacherInfoResponse(BaseModel):
    """Ответ с информацией о преподавателе"""
    success: bool
    departments: Optional[List[str]] = None
    photo: Optional[str] = None
    error: Optional[str] = None


class ScheduleRequest(BaseModel):
    """Запрос на получение расписания"""
    student_email: EmailStr
    week: int = Field(1, description="Номер недели (1 = текущая, 2 = следующая)")


class ScheduleResponse(BaseModel):
    """Ответ с расписанием"""
    success: bool
    schedule: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None


class ContactsRequest(BaseModel):
    """Запрос на получение контактов"""
    student_email: EmailStr


class ContactsResponse(BaseModel):
    """Ответ с контактами"""
    success: bool
    deans: Optional[List[Dict[str, str]]] = None
    departments: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None


class PlatformsResponse(BaseModel):
    """Ответ со списком платформ"""
    success: bool
    platforms: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None


class ServicesResponse(BaseModel):
    """Ответ со списком сервисов"""
    success: bool
    services: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None


class MapsResponse(BaseModel):
    """Ответ со списком карт корпусов"""
    buildings: List[Dict] = Field(default_factory=list, description="Список корпусов с картами")


def get_university_id_from_header(x_university_id: Optional[str] = Header(None, alias="X-University-Id")) -> int:
    """Получить university_id из заголовка запроса"""
    if not x_university_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заголовок X-University-Id обязателен"
        )
    try:
        return int(x_university_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат university_id"
        )


@router.post("/login", response_model=LoginResponse)
async def login_student(
    request: LoginRequest,
    db: Session = Depends(get_db),
    university_id: int = Depends(get_university_id_from_header)
):
    """Логин студента (симуляция - всегда успешен)"""
    # В Ghost API логин всегда успешен, так как данные уже в БД
    # Проверяем, существует ли студент
    student_repo = StudentRepository(db)
    student = student_repo.get_by_email(university_id, request.student_email)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Студент не найден"
        )
    
    return LoginResponse(success=True, error=None)


@router.post("/teachers", response_model=TeachersResponse)
async def get_teachers(
    request: TeachersRequest,
    db: Session = Depends(get_db),
    university_id: int = Depends(get_university_id_from_header)
):
    """Получить список преподавателей"""
    teacher_repo = TeacherRepository(db)
    teachers = teacher_repo.get_all_by_university(university_id)
    
    teachers_list = [
        {"id": teacher.teacher_id, "name": teacher.name}
        for teacher in teachers
    ]
    
    return TeachersResponse(
        success=True,
        teachers=teachers_list,
        error=None
    )


@router.post("/personal_data", response_model=PersonalDataResponse)
async def get_personal_data(
    request: PersonalDataRequest,
    db: Session = Depends(get_db),
    university_id: int = Depends(get_university_id_from_header)
):
    """Получить данные студента"""
    student_repo = StudentRepository(db)
    student = student_repo.get_by_email(university_id, request.student_email)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Студент не найден"
        )
    
    data = {
        "full_name": student.full_name,
        "group": student.group,
        "course": student.course,
        "photo": student.photo
    }
    
    return PersonalDataResponse(success=True, data=data, error=None)


@router.post("/teacher_info", response_model=TeacherInfoResponse)
async def get_teacher_info(
    request: TeacherInfoRequest,
    db: Session = Depends(get_db),
    university_id: int = Depends(get_university_id_from_header)
):
    """Получить информацию о преподавателе"""
    teacher_repo = TeacherRepository(db)
    
    # Извлекаем номер преподавателя (может быть "tech2173" или "2173")
    teacher_id = request.teacher_id
    if teacher_id.startswith('tech'):
        teacher_id = teacher_id[4:]
    
    teacher = teacher_repo.get_by_id(university_id, teacher_id)
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Преподаватель не найден"
        )
    
    # Парсим departments из JSON строки
    departments = []
    if teacher.departments:
        try:
            departments = json.loads(teacher.departments)
        except (json.JSONDecodeError, TypeError):
            departments = []
    
    return TeacherInfoResponse(
        success=True,
        departments=departments,
        photo=teacher.photo,
        error=None
    )


@router.post("/schedule", response_model=ScheduleResponse)
async def get_schedule(
    request: ScheduleRequest,
    db: Session = Depends(get_db),
    university_id: int = Depends(get_university_id_from_header)
):
    """Получить расписание студента"""
    schedule_repo = ScheduleRepository(db)
    schedules = schedule_repo.get_by_student_and_week(
        university_id,
        request.student_email,
        request.week
    )
    
    schedule_list = []
    for schedule in schedules:
        schedule_list.append({
            "date": schedule.date.isoformat() if schedule.date else None,
            "time_start": schedule.time_start.strftime("%H:%M") if schedule.time_start else None,
            "time_end": schedule.time_end.strftime("%H:%M") if schedule.time_end else None,
            "subject": schedule.subject,
            "type": schedule.type,
            "teacher": schedule.teacher,
            "room": schedule.room
        })
    
    return ScheduleResponse(success=True, schedule=schedule_list, error=None)


@router.post("/contacts", response_model=ContactsResponse)
async def get_contacts(
    request: ContactsRequest,
    db: Session = Depends(get_db),
    university_id: int = Depends(get_university_id_from_header)
):
    """Получить контакты деканатов и кафедр"""
    contact_repo = ContactRepository(db)
    
    deans = contact_repo.get_all_deans(university_id)
    departments = contact_repo.get_all_departments(university_id)
    
    deans_list = [
        {
            "faculty": dean.faculty,
            "phone": dean.phone,
            "email": dean.email
        }
        for dean in deans
    ]
    
    departments_list = [
        {
            "faculty": dept.faculty,
            "department": dept.department,
            "phones": dept.phones,
            "email": dept.email
        }
        for dept in departments
    ]
    
    return ContactsResponse(
        success=True,
        deans=deans_list,
        departments=departments_list,
        error=None
    )


@router.get("/platforms", response_model=PlatformsResponse)
async def get_platforms(
    db: Session = Depends(get_db),
    university_id: int = Depends(get_university_id_from_header)
):
    """Получить список платформ"""
    platform_repo = PlatformRepository(db)
    platforms = platform_repo.get_all_by_university(university_id)
    
    platforms_list = [
        {
            "key": platform.key,
            "name": platform.name,
            "url": platform.url,
            "emoji": platform.emoji
        }
        for platform in platforms
    ]
    
    return PlatformsResponse(success=True, platforms=platforms_list, error=None)


@router.get("/services", response_model=ServicesResponse)
async def get_services():
    """Получить список сервисов (статический список)"""
    services = [
        {"key": "schedule", "name": "Расписание", "emoji": "📅"},
        {"key": "teachers", "name": "Преподаватели", "emoji": "👨‍🏫"},
        {"key": "map", "name": "Карта", "emoji": "🗺️"},
        {"key": "contacts", "name": "Контакты", "emoji": "📞"},
        {"key": "chats", "name": "Чаты", "emoji": "💬"}
    ]
    
    return ServicesResponse(success=True, services=services, error=None)


@router.get("/maps", response_model=MapsResponse)
async def get_maps():
    """Получить список карт корпусов
    
    Получает список всех корпусов университета с их координатами и ссылками на карты.
    Данные загружаются из JSON файла.
    Не требует аутентификации.
    
    **Возвращает:**
    - `buildings`: Список корпусов, каждый содержит:
      - `name`: Название корпуса
      - `latitude`: Широта
      - `longitude`: Долгота
      - `yandex_map_url`: Ссылка на Яндекс карты (опционально)
      - `gis2_map_url`: Ссылка на 2ГИС карты (опционально)
      - `google_map_url`: Ссылка на Google карты (опционально)
    """
    import os
    import json
    
    # Путь к файлу с данными о картах
    maps_data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'maps.json')
    maps_data_file = os.path.normpath(maps_data_file)
    
    try:
        if not os.path.exists(maps_data_file):
            # Возвращаем пустой список, если файл не найден
            return MapsResponse(buildings=[])
        
        with open(maps_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            buildings = data.get('buildings', [])
            return MapsResponse(buildings=buildings)
    except (json.JSONDecodeError, IOError) as e:
        # В случае ошибки возвращаем пустой список
        return MapsResponse(buildings=[])

