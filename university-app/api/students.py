from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from services.university_scraper import UniversityScraper
from repositories.session_cookies_repository import SessionCookiesRepository
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
import json

router = APIRouter()


class LoginRequest(BaseModel):
    """Запрос на логин студента на сайте университета
    
    Выполняет логин на обоих сайтах университета (tt.chuvsu.ru и lk.chuvsu.ru)
    и сохраняет cookies сессии в БД.
    """
    student_email: EmailStr = Field(..., description="Email студента для входа на сайт университета", example="student@university.ru")
    password: str = Field(..., description="Пароль студента для входа на сайт университета", example="password123")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_email": "student@university.ru",
                "password": "password123"
            }
        }


class LoginResponse(BaseModel):
    """Ответ на запрос логина студента
    
    Содержит результат попытки логина. Cookies сессии сохраняются в БД и не возвращаются в ответе.
    """
    success: bool = Field(..., description="Успешность операции логина", example=True)
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "error": None
            }
        }


class TeachersRequest(BaseModel):
    """Запрос на получение списка преподавателей
    
    Получает список всех преподавателей университета для студента.
    """
    student_email: EmailStr = Field(..., description="Email студента", example="student@university.ru")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_email": "student@university.ru"
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


class PersonalDataRequest(BaseModel):
    """Запрос на получение данных студента
    
    Получает структурированные данные студента с личного кабинета университета.
    """
    student_email: EmailStr = Field(..., description="Email студента", example="student@university.ru")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_email": "student@university.ru"
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


class TeacherInfoRequest(BaseModel):
    """Запрос на получение информации о преподавателе
    
    Получает информацию о конкретном преподавателе (кафедры, фото).
    """
    student_email: EmailStr = Field(..., description="Email студента", example="student@university.ru")
    teacher_id: str = Field(..., description="ID преподавателя (номер после \"tech\", например \"0000\" или \"2173\")", example="2173")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_email": "student@university.ru",
                "teacher_id": "2173"
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


class ScheduleRequest(BaseModel):
    """Запрос на получение расписания студента
    
    Получает расписание занятий студента за указанный период.
    """
    student_email: EmailStr = Field(..., description="Email студента", example="student@university.ru")
    date_range: str = Field(..., description="Промежуток дней в формате ДД.ММ-ДД.ММ (например: 10.11-03.12) или один день (например: 04.11)", example="10.11-03.12")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_email": "student@university.ru",
                "date_range": "10.11-03.12"
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


class ContactsRequest(BaseModel):
    """Запрос на получение контактов деканатов и кафедр
    
    Получает контактную информацию деканатов факультетов и кафедр.
    """
    student_email: EmailStr = Field(..., description="Email студента", example="student@university.ru")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_email": "student@university.ru"
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
    platforms: Optional[list] = Field(None, description="Список платформ: [{\"key\": \"moodle\", \"name\": \"Moodle\", \"url\": \"https://moodle.university.ru\", \"emoji\": \"📚\"}, ...]", example=[{"key": "requests", "name": "Запросы и справки", "url": "https://lk.chuvsu.ru/student/request.php", "emoji": "📋"}, {"key": "practice", "name": "Практика", "url": "https://lk.chuvsu.ru/student/practic.php", "emoji": "💼"}])
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "platforms": [
                    {"key": "requests", "name": "Запросы и справки", "url": "https://lk.chuvsu.ru/student/request.php", "emoji": "📋"},
                    {"key": "practice", "name": "Практика", "url": "https://lk.chuvsu.ru/student/practic.php", "emoji": "💼"}
                ],
                "error": None
            }
        }


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Логин студента",
    description="Выполняет логин на обоих сайтах университета (tt.chuvsu.ru и lk.chuvsu.ru) и сохраняет cookies сессии в БД. Cookies не возвращаются в ответе - они используются только внутри University API для последующих запросов. При успешном логине возвращает только success=true, при ошибке - HTTP 401.",
    response_description="Результат операции логина (success/error). Cookies сохраняются в БД и не возвращаются.",
    responses={
        200: {"description": "Логин успешен. Возвращает только success=true. Cookies сохраняются в БД и не возвращаются."},
        401: {"description": "Неверный email или пароль"}
    }
)
async def login_student(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Выполнить логин студента на сайте университета
    
    Выполняет логин на обоих сайтах университета (tt.chuvsu.ru и lk.chuvsu.ru)
    и сохраняет cookies сессии по доменам в БД, связанные с student_email.
    Cookies не возвращаются в ответе - они используются только внутри University API
    для последующих запросов (получение данных студента, расписания и т.д.).
    
    **Параметры:**
    - `student_email`: Email студента для входа на сайт университета
    - `password`: Пароль студента для входа на сайт университета
    
    **Возвращает:**
    - `success`: Успешность операции логина (true/false)
    - `error`: Сообщение об ошибке (если есть)
    
    **Примечание:**
    Cookies автоматически сохраняются в БД и используются для последующих запросов.
    Они не возвращаются в ответе для безопасности.
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8002/students/login",
        json={
            "student_email": "student@university.ru",
            "password": "password123"
        }
    )
    
    # Ответ: {"success": True, "error": None}
    # Cookies сохраняются в БД и не возвращаются
    ```
    """
    scraper = UniversityScraper()
    cookies_repo = SessionCookiesRepository(db)
    
    # Специальная обработка тестового аккаунта
    # test@test.ru/test использует реальные учетные данные goliluxa@mail.ru/P17133p17133
    actual_email = request.student_email
    actual_password = request.password
    
    if request.student_email.lower() == "test@test.ru" and request.password == "test":
        actual_email = "goliluxa@mail.ru"
        actual_password = "P17133p17133"
    
    login_result = scraper.login_both_sites(actual_email, actual_password)
    
    if not login_result["success"]:
        # Возвращаем ошибку логина с HTTP 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=login_result.get("error", "Неверный email или пароль")
        )
    
    # Сохраняем cookies в БД под исходным student_email (test@test.ru)
    # Это позволяет использовать test@test.ru в других запросах
    cookies_by_domain = login_result.get("cookies_by_domain", {})
    cookies_json = json.dumps(cookies_by_domain)
    cookies_repo.create_or_update(request.student_email, cookies_json)
    
    # Возвращаем только success - cookies не возвращаем
    return LoginResponse(
        success=True,
        error=None
    )


@router.post(
    "/teachers",
    response_model=TeachersResponse,
    summary="Получить список преподавателей",
    description="Получает список всех преподавателей университета для студента. Использует сохраненные cookies сессии из БД.",
    response_description="Список преподавателей с их ID и ФИО",
    responses={
        200: {"description": "Список преподавателей успешно получен"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Cookies не найдены (необходимо сначала выполнить логин)"}
    }
)
async def get_teachers(
    request: TeachersRequest,
    db: Session = Depends(get_db)
):
    """Получить список преподавателей
    
    Получает список всех преподавателей университета для студента.
    Использует сохраненные cookies сессии из БД для доступа к сайту университета.
    
    **Параметры:**
    - `student_email`: Email студента
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8002/students/teachers",
        json={
            "student_email": "student@university.ru"
        }
    )
    ```
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


@router.post(
    "/personal_data",
    response_model=PersonalDataResponse,
    summary="Получить данные студента",
    description="Получает структурированные данные студента с личного кабинета университета (ФИО, группа, курс, фото и т.д.). Использует сохраненные cookies сессии из БД.",
    response_description="Структурированные данные студента",
    responses={
        200: {"description": "Данные студента успешно получены"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Cookies не найдены (необходимо сначала выполнить логин)"}
    }
)
async def get_student_personal_data(
    request: PersonalDataRequest,
    db: Session = Depends(get_db)
):
    """Получить данные студента
    
    Получает структурированные данные студента с личного кабинета университета
    (ФИО, группа, курс, фото и т.д.).
    Использует сохраненные cookies сессии из БД для доступа к сайту университета.
    
    **Параметры:**
    - `student_email`: Email студента
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8002/students/personal_data",
        json={
            "student_email": "student@university.ru"
        }
    )
    ```
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


@router.post(
    "/teacher_info",
    response_model=TeacherInfoResponse,
    summary="Получить информацию о преподавателе",
    description="Получает информацию о конкретном преподавателе (кафедры, фото). Использует сохраненные cookies сессии из БД.",
    response_description="Информация о преподавателе (кафедры и фото)",
    responses={
        200: {"description": "Информация о преподавателе успешно получена"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Cookies не найдены (необходимо сначала выполнить логин)"}
    }
)
async def get_teacher_info(
    request: TeacherInfoRequest,
    db: Session = Depends(get_db)
):
    """Получить информацию о преподавателе
    
    Получает информацию о конкретном преподавателе (кафедры, фото).
    Использует сохраненные cookies сессии из БД для доступа к сайту университета.
    
    **Параметры:**
    - `student_email`: Email студента
    - `teacher_id`: ID преподавателя (номер после "tech", например "0000" или "2173")
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8002/students/teacher_info",
        json={
            "student_email": "student@university.ru",
            "teacher_id": "2173"
        }
    )
    ```
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


@router.post(
    "/schedule",
    response_model=ScheduleResponse,
    summary="Получить расписание студента",
    description="Получает расписание занятий студента за указанный период. Использует сохраненные cookies сессии из БД.",
    response_description="Расписание занятий студента",
    responses={
        200: {"description": "Расписание успешно получено"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Cookies не найдены (необходимо сначала выполнить логин)"}
    }
)
async def get_schedule(
    request: ScheduleRequest,
    db: Session = Depends(get_db)
):
    """Получить расписание студента
    
    Получает расписание занятий студента за указанный период.
    Использует сохраненные cookies сессии из БД для доступа к сайту университета.
    
    **Параметры:**
    - `student_email`: Email студента
    - `date_range`: Промежуток дней в формате ДД.ММ-ДД.ММ (например: 10.11-03.12) или один день (например: 04.11)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Получить расписание за период с 10 ноября по 3 декабря
    response = requests.post(
        "http://localhost:8002/students/schedule",
        json={
            "student_email": "student@university.ru",
            "date_range": "10.11-03.12"
        }
    )
    ```
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[UNIVERSITY_API] Начало получения расписания: student_email={request.student_email}, date_range={request.date_range}")
    
    scraper = UniversityScraper()
    cookies_repo = SessionCookiesRepository(db)
    
    # Получаем cookies из БД
    logger.info(f"[UNIVERSITY_API] Получаем cookies из БД для student_email={request.student_email}")
    session_cookies = cookies_repo.get_by_email(request.student_email)
    if not session_cookies:
        logger.error(f"[UNIVERSITY_API] Cookies не найдены для student_email={request.student_email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cookies не найдены. Необходимо выполнить логин."
        )
    logger.info(f"[UNIVERSITY_API] Cookies найдены в БД")
    
    # Парсим cookies_by_domain
    logger.info(f"[UNIVERSITY_API] Парсим cookies_by_domain")
    lk_cookies = None  # Инициализируем как None
    try:
        cookies_by_domain = json.loads(session_cookies.cookies_by_domain)
        logger.info(f"[UNIVERSITY_API] Cookies_by_domain распарсен, домены: {list(cookies_by_domain.keys())}")
        # Для расписания нужны cookies от tt.chuvsu.ru
        tt_cookies = cookies_by_domain.get("tt.chuvsu.ru")
        if not tt_cookies:
            logger.error(f"[UNIVERSITY_API] Cookies для tt.chuvsu.ru не найдены")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cookies для tt.chuvsu.ru не найдены. Необходимо повторно выполнить логин."
            )
        logger.info(f"[UNIVERSITY_API] Cookies для tt.chuvsu.ru найдены")
        
        # Для получения personal_data нужны cookies от lk.chuvsu.ru
        lk_cookies = cookies_by_domain.get("lk.chuvsu.ru")
        if not lk_cookies:
            logger.warning(f"[UNIVERSITY_API] Cookies для lk.chuvsu.ru не найдены, будет использован fallback")
        else:
            logger.info(f"[UNIVERSITY_API] Cookies для lk.chuvsu.ru найдены")
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"[UNIVERSITY_API] Ошибка при парсинге cookies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при чтении cookies из БД"
        )
    
    # Обновляем время последнего использования
    logger.info(f"[UNIVERSITY_API] Обновляем время последнего использования cookies")
    cookies_repo.update_last_used(request.student_email)
    
    logger.info(f"[UNIVERSITY_API] Вызываем scraper.get_schedule: date_range={request.date_range}")
    result = scraper.get_schedule(date_range=request.date_range, cookies_json=tt_cookies, lk_cookies_json=lk_cookies)
    logger.info(f"[UNIVERSITY_API] Scraper вернул результат: success={result.get('success')}, schedule_items={len(result.get('schedule', [])) if result.get('schedule') else 0}")
    
    if not result["success"]:
        error_msg = result.get("error", "Не удалось получить расписание")
        logger.error(f"[UNIVERSITY_API] Scraper вернул ошибку: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg
        )
    
    schedule_count = len(result.get("schedule", []))
    logger.info(f"[UNIVERSITY_API] Успешно получено расписание: {schedule_count} занятий")
    
    return ScheduleResponse(
        success=True,
        schedule=result.get("schedule"),
        error=None
    )


@router.post(
    "/contacts",
    response_model=ContactsResponse,
    summary="Получить контакты деканатов и кафедр",
    description="Получает контактную информацию деканатов факультетов и кафедр. Использует сохраненные cookies сессии из БД.",
    response_description="Контакты деканатов и кафедр",
    responses={
        200: {"description": "Контакты успешно получены"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Cookies не найдены (необходимо сначала выполнить логин)"}
    }
)
async def get_contacts(
    request: ContactsRequest,
    db: Session = Depends(get_db)
):
    """Получить контакты деканатов и кафедр
    
    Получает контактную информацию деканатов факультетов и кафедр.
    Использует сохраненные cookies сессии из БД для доступа к сайту университета.
    
    **Параметры:**
    - `student_email`: Email студента
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8002/students/contacts",
        json={
            "student_email": "student@university.ru"
        }
    )
    ```
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


@router.get(
    "/platforms",
    response_model=PlatformsResponse,
    summary="Получить список веб-платформ",
    description="Получает список полезных веб-платформ университета для студентов. Возвращает статический список платформ.",
    response_description="Список полезных веб-платформ",
    responses={
        200: {"description": "Список платформ успешно получен"}
    }
)
async def get_platforms():
    """Получить список полезных веб-платформ
    
    Получает список полезных веб-платформ университета для студентов.
    Возвращает статический список платформ с ключами, названиями и ссылками.
    Не требует аутентификации.
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8002/students/platforms")
    ```
    """
    platforms = [
        {
            "key": "requests",
            "name": "Запросы и справки",
            "url": "https://lk.chuvsu.ru/student/request.php",
            "emoji": "📋"
        },
        {
            "key": "practice",
            "name": "Практика",
            "url": "https://lk.chuvsu.ru/student/practic.php",
            "emoji": "💼"
        },
        {
            "key": "portfolio",
            "name": "Зачетная книжка",
            "url": "https://lk.chuvsu.ru/portfolio/index.php",
            "emoji": "📖"
        },
        {
            "key": "links",
            "name": "Полезные ссылки",
            "url": "https://lk.chuvsu.ru/student/links.php",
            "emoji": "🔗"
        }
    ]
    
    return PlatformsResponse(
        success=True,
        platforms=platforms,
        error=None
    )


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


class NewsResponse(BaseModel):
    """Ответ со списком новостей"""
    success: bool = Field(..., description="Успешность операции", example=True)
    news: Optional[list] = Field(None, description="Список новостей", example=[])
    error: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)", example=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "news": [
                    {
                        "id": "news_1",
                        "title": "Открытие нового учебного корпуса",
                        "content": "Университет рад сообщить об открытии нового современного учебного корпуса...",
                        "date": "15.12.2024",
                        "author": "Администрация университета",
                        "category": "Общие новости",
                        "image_url": None,
                        "link": "https://www.chuvsu.ru/news/1"
                    }
                ],
                "error": None
            }
        }


@router.get(
    "/maps",
    response_model=MapsResponse,
    summary="Получить список карт корпусов",
    description="Получает список всех корпусов университета с их координатами и ссылками на карты (Яндекс, 2ГИС, Google). Не требует аутентификации.",
    response_description="Список корпусов с картами",
    responses={
        200: {"description": "Список карт успешно получен"}
    }
)
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
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8002/students/maps")
    maps = response.json()
    ```
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


@router.get(
    "/services",
    response_model=ServicesResponse,
    summary="Получить список сервисов",
    description="Получает список сервисов университета для студентов (не веб-платформы). Возвращает статический список сервисов с названиями и эмодзи.",
    response_description="Список сервисов",
    responses={
        200: {"description": "Список сервисов успешно получен"}
    }
)
async def get_services():
    """Получить список сервисов
    
    Получает список сервисов университета для студентов (не веб-платформы).
    Возвращает статический список сервисов с названиями и эмодзи.
    Не требует аутентификации.
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8002/students/services")
    ```
    """
    services = [
        {
            "key": "schedule",
            "name": "Расписание",
            "emoji": "📅"
        },
        {
            "key": "teachers",
            "name": "Преподаватели",
            "emoji": "👨‍🏫"
        },
        {
            "key": "map",
            "name": "Карта",
            "emoji": "🗺️"
        },
        {
            "key": "contacts",
            "name": "Контакты",
            "emoji": "📞"
        },
        {
            "key": "chats",
            "name": "Чаты",
            "emoji": "💬"
        }
    ]
    
    return ServicesResponse(
        success=True,
        services=services,
        error=None
    )


@router.get(
    "/news",
    response_model=NewsResponse,
    summary="Получить список новостей",
    description="Получает список новостей университета. Использует тестовые данные из JSON файла. Не требует аутентификации.",
    response_description="Список новостей",
    responses={
        200: {"description": "Список новостей успешно получен"}
    }
)
async def get_news(limit: int = 10, db: Session = Depends(get_db)):
    """Получить список новостей
    
    Получает список новостей университета.
    Данные загружаются из тестового JSON файла.
    Не требует аутентификации.
    
    **Параметры:**
    - `limit`: Максимальное количество новостей для возврата (по умолчанию 10)
    
    **Возвращает:**
    - `success`: Успешность операции
    - `news`: Список новостей, каждая содержит:
      - `id`: Уникальный идентификатор новости
      - `title`: Заголовок новости
      - `content`: Содержание новости
      - `date`: Дата публикации (формат ДД.ММ.ГГГГ)
      - `author`: Автор новости
      - `category`: Категория новости
      - `image_url`: URL изображения (опционально)
      - `link`: Ссылка на полную новость
    - `error`: Сообщение об ошибке (если есть)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Получить 10 новостей (по умолчанию)
    response = requests.get("http://localhost:8002/students/news")
    
    # Получить 5 новостей
    response = requests.get("http://localhost:8002/students/news?limit=5")
    ```
    """
    try:
        scraper = UniversityScraper()
        result = scraper.get_news(limit=limit)
        
        if result.get("success"):
            return NewsResponse(
                success=True,
                news=result.get("news", []),
                error=None
            )
        else:
            return NewsResponse(
                success=False,
                news=None,
                error=result.get("error", "Неизвестная ошибка")
            )
    except Exception as e:
        return NewsResponse(
            success=False,
            news=None,
            error=f"Ошибка при получении новостей: {str(e)}"
        )
