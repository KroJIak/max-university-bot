from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from services.university_scraper import UniversityScraper
from repositories.session_cookies_repository import SessionCookiesRepository
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import json

router = APIRouter()


class LoginRequest(BaseModel):
    """Запрос на логин студента"""
    student_email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Ответ на запрос логина"""
    success: bool
    cookies_by_domain: Optional[Dict[str, Optional[str]]] = None  # {"tt.chuvsu.ru": "...", "lk.chuvsu.ru": "..."}
    error: Optional[str] = None


class TeachersRequest(BaseModel):
    """Запрос на получение списка преподавателей"""
    student_email: EmailStr


class TeachersResponse(BaseModel):
    """Ответ со списком преподавателей"""
    success: bool
    teachers: Optional[list] = None  # Список преподавателей: [{"id": "tech0001", "name": "ФИО"}, ...]
    error: Optional[str] = None


class PersonalDataRequest(BaseModel):
    """Запрос на получение данных студента"""
    student_email: EmailStr


class PersonalDataResponse(BaseModel):
    """Ответ с данными студента"""
    success: bool
    data: Optional[Dict[str, Optional[str]]] = None  # Структурированные данные студента
    error: Optional[str] = None


class TeacherInfoRequest(BaseModel):
    """Запрос на получение информации о преподавателе"""
    student_email: EmailStr
    teacher_id: str  # ID преподавателя (номер после "tech", например "0000" или "2173")


class TeacherInfoResponse(BaseModel):
    """Ответ с информацией о преподавателе"""
    success: bool
    departments: Optional[list] = None  # Список кафедр
    photo: Optional[str] = None  # Фото в формате base64 data URI
    error: Optional[str] = None


class ScheduleRequest(BaseModel):
    """Запрос на получение расписания"""
    student_email: EmailStr
    week: int = 1  # 1 = текущая неделя, 2 = следующая неделя


class ScheduleResponse(BaseModel):
    """Ответ с расписанием"""
    success: bool
    schedule: Optional[list] = None  # Список занятий
    error: Optional[str] = None


class ContactsRequest(BaseModel):
    """Запрос на получение контактов"""
    student_email: EmailStr


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


@router.post("/login", response_model=LoginResponse)
async def login_student(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Выполнить логин на обоих сайтах университета (tt.chuvsu.ru и lk.chuvsu.ru)
    
    Сохраняет cookies сессии по доменам в БД, связанные с student_email
    """
    scraper = UniversityScraper()
    cookies_repo = SessionCookiesRepository(db)
    
    login_result = scraper.login_both_sites(request.student_email, request.password)
    
    if not login_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=login_result.get("error", "Неверный email или пароль")
        )
    
    # Сохраняем cookies в БД
    cookies_by_domain = login_result.get("cookies_by_domain", {})
    cookies_json = json.dumps(cookies_by_domain)
    cookies_repo.create_or_update(request.student_email, cookies_json)
    
    return LoginResponse(
        success=True,
        cookies_by_domain=cookies_by_domain,
        error=None
    )


@router.post("/teachers", response_model=TeachersResponse)
async def get_teachers(
    request: TeachersRequest,
    db: Session = Depends(get_db)
):
    """
    Получить список преподавателей
    
    Получает cookies из БД по student_email и использует cookies для tt.chuvsu.ru
    Парсит страницу https://tt.chuvsu.ru/index/tech и возвращает список преподавателей
    """
    scraper = UniversityScraper()
    cookies_repo = SessionCookiesRepository(db)
    
    # Получаем cookies из БД
    session_cookies = cookies_repo.get_by_email(request.student_email)
    if not session_cookies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cookies не найдены. Необходимо выполнить логин."
        )
    
    # Парсим cookies_by_domain
    try:
        cookies_by_domain = json.loads(session_cookies.cookies_by_domain)
        tt_cookies = cookies_by_domain.get("tt.chuvsu.ru")
        if not tt_cookies:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cookies для tt.chuvsu.ru не найдены. Необходимо повторно выполнить логин."
            )
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при чтении cookies из БД"
        )
    
    # Обновляем время последнего использования
    cookies_repo.update_last_used(request.student_email)
    
    result = scraper.get_tech_page(cookies_json=tt_cookies)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить страницу")
        )
    
    return TeachersResponse(
        success=True,
        teachers=result.get("teachers"),
        error=None
    )


@router.post("/personal_data", response_model=PersonalDataResponse)
async def get_student_personal_data(
    request: PersonalDataRequest,
    db: Session = Depends(get_db)
):
    """
    Получить данные студента с https://lk.chuvsu.ru/student/personal_data.php
    
    Получает cookies из БД по student_email и использует cookies для lk.chuvsu.ru
    Если cookies для lk.chuvsu.ru нет, пробует использовать cookies от tt.chuvsu.ru
    """
    scraper = UniversityScraper()
    cookies_repo = SessionCookiesRepository(db)
    
    # Получаем cookies из БД
    session_cookies = cookies_repo.get_by_email(request.student_email)
    if not session_cookies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cookies не найдены. Необходимо выполнить логин."
        )
    
    # Парсим cookies_by_domain
    try:
        cookies_by_domain = json.loads(session_cookies.cookies_by_domain)
        lk_cookies = cookies_by_domain.get("lk.chuvsu.ru")
        if not lk_cookies:
            # Пробуем использовать cookies от tt как fallback
            lk_cookies = cookies_by_domain.get("tt.chuvsu.ru")
            if not lk_cookies:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Cookies для lk.chuvsu.ru не найдены. Необходимо повторно выполнить логин."
                )
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при чтении cookies из БД"
        )
    
    # Обновляем время последнего использования
    cookies_repo.update_last_used(request.student_email)
    
    result = scraper.get_student_personal_data(cookies_json=lk_cookies)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить данные студента")
        )
    
    return PersonalDataResponse(
        success=True,
        data=result.get("data"),
        error=None
    )


@router.post("/teacher_info", response_model=TeacherInfoResponse)
async def get_teacher_info(
    request: TeacherInfoRequest,
    db: Session = Depends(get_db)
):
    """
    Получить информацию о преподавателе со страницы https://tt.chuvsu.ru/index/techtt/tech/{teacher_id}
    
    Получает cookies из БД по student_email и использует cookies для tt.chuvsu.ru
    Извлекает кафедры и фото преподавателя
    """
    scraper = UniversityScraper()
    cookies_repo = SessionCookiesRepository(db)
    
    # Получаем cookies из БД
    session_cookies = cookies_repo.get_by_email(request.student_email)
    if not session_cookies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cookies не найдены. Необходимо выполнить логин."
        )
    
    # Парсим cookies_by_domain
    try:
        cookies_by_domain = json.loads(session_cookies.cookies_by_domain)
        tt_cookies = cookies_by_domain.get("tt.chuvsu.ru")
        if not tt_cookies:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cookies для tt.chuvsu.ru не найдены. Необходимо повторно выполнить логин."
            )
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при чтении cookies из БД"
        )
    
    # Обновляем время последнего использования
    cookies_repo.update_last_used(request.student_email)
    
    # Извлекаем номер преподавателя из teacher_id (может быть "tech2173" или "2173")
    teacher_number = request.teacher_id
    if teacher_number.startswith('tech'):
        teacher_number = teacher_number[4:]  # Убираем префикс "tech"
    
    result = scraper.get_teacher_info(teacher_id=teacher_number, cookies_json=tt_cookies)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить информацию о преподавателе")
        )
    
    return TeacherInfoResponse(
        success=True,
        departments=result.get("departments"),
        photo=result.get("photo"),
        error=None
    )


@router.post("/schedule", response_model=ScheduleResponse)
async def get_schedule(
    request: ScheduleRequest,
    db: Session = Depends(get_db)
):
    """
    Получить расписание со страницы https://lk.chuvsu.ru/student/tt.php
    
    Получает cookies из БД по student_email и использует cookies для lk.chuvsu.ru
    Парсит HTML таблицу и возвращает структурированное расписание
    """
    scraper = UniversityScraper()
    cookies_repo = SessionCookiesRepository(db)
    
    # Получаем cookies из БД
    session_cookies = cookies_repo.get_by_email(request.student_email)
    if not session_cookies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cookies не найдены. Необходимо выполнить логин."
        )
    
    # Парсим cookies_by_domain
    try:
        cookies_by_domain = json.loads(session_cookies.cookies_by_domain)
        lk_cookies = cookies_by_domain.get("lk.chuvsu.ru")
        if not lk_cookies:
            # Пробуем использовать cookies от tt как fallback
            lk_cookies = cookies_by_domain.get("tt.chuvsu.ru")
            if not lk_cookies:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Cookies для lk.chuvsu.ru не найдены. Необходимо повторно выполнить логин."
                )
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при чтении cookies из БД"
        )
    
    # Обновляем время последнего использования
    cookies_repo.update_last_used(request.student_email)
    
    result = scraper.get_schedule(week=request.week, cookies_json=lk_cookies)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить расписание")
        )
    
    return ScheduleResponse(
        success=True,
        schedule=result.get("schedule"),
        error=None
    )


@router.post("/contacts", response_model=ContactsResponse)
async def get_contacts(
    request: ContactsRequest,
    db: Session = Depends(get_db)
):
    """
    Получить контакты деканатов и кафедр со страницы https://lk.chuvsu.ru/student/contacts.php
    
    Получает cookies из БД по student_email и использует cookies для lk.chuvsu.ru
    Парсит HTML страницу и возвращает структурированные контакты
    """
    scraper = UniversityScraper()
    cookies_repo = SessionCookiesRepository(db)
    
    # Получаем cookies из БД
    session_cookies = cookies_repo.get_by_email(request.student_email)
    if not session_cookies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cookies не найдены. Необходимо выполнить логин."
        )
    
    # Парсим cookies_by_domain
    try:
        cookies_by_domain = json.loads(session_cookies.cookies_by_domain)
        lk_cookies = cookies_by_domain.get("lk.chuvsu.ru")
        if not lk_cookies:
            # Пробуем использовать cookies от tt как fallback
            lk_cookies = cookies_by_domain.get("tt.chuvsu.ru")
            if not lk_cookies:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Cookies для lk.chuvsu.ru не найдены. Необходимо повторно выполнить логин."
                )
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при чтении cookies из БД"
        )
    
    # Обновляем время последнего использования
    cookies_repo.update_last_used(request.student_email)
    
    result = scraper.get_contacts(cookies_json=lk_cookies)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить контакты")
        )
    
    return ContactsResponse(
        success=True,
        deans=result.get("deans"),
        departments=result.get("departments"),
        error=None
    )


@router.get("/platforms", response_model=PlatformsResponse)
async def get_platforms():
    """
    Получить список полезных веб-платформ
    
    Возвращает статический список платформ с ключами, названиями и ссылками
    """
    platforms = [
        {
            "key": "requests",
            "name": "Запросы и справки",
            "url": "https://lk.chuvsu.ru/student/request.php"
        },
        {
            "key": "practice",
            "name": "Практика",
            "url": "https://lk.chuvsu.ru/student/practic.php"
        },
        {
            "key": "portfolio",
            "name": "Зачетная книжка",
            "url": "https://lk.chuvsu.ru/portfolio/index.php"
        },
        {
            "key": "links",
            "name": "Полезные ссылки",
            "url": "https://lk.chuvsu.ru/student/links.php"
        }
    ]
    
    return PlatformsResponse(
        success=True,
        platforms=platforms,
        error=None
    )
