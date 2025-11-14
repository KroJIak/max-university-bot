"""Роутеры для работы со студентами"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from repositories.student_credentials_repository import StudentCredentialsRepository
from repositories.user_repository import UserRepository
from api.v1.schemas.students import (
    StudentLoginRequest,
    StudentLoginResponse,
    StudentStatusResponse,
    StudentCredentialsResponse,
    StudentCredentialsUpdate,
    TeachersResponse,
    PersonalDataResponse,
    TeacherInfoResponse,
    ScheduleResponse,
    ContactsResponse,
    PlatformsResponse,
    ServicesResponse
)
from api.v1.services.university_config import get_university_config
from api.v1.services.students_service import (
    validate_university_api_config,
    perform_login,
    save_student_credentials,
    validate_student_email_uniqueness
)
from api.v1.services.university_api_client import (
    call_university_api_login,
    call_university_api_tech,
    call_university_api_personal_data,
    call_university_api_teacher_info,
    call_university_api_schedule,
    call_university_api_contacts,
    call_university_api_platforms,
    call_university_api_services
)
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_university_id_from_user(db: Session, user_id: int) -> int:
    """Получить university_id из user_id
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
    
    Returns:
        university_id
    
    Raises:
        HTTPException: Если пользователь не найден
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_user_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user.university_id


@router.post(
    "/students/login",
    response_model=StudentLoginResponse,
    summary="Логин студента",
    description="Выполняет логин на сайте университета с использованием credentials студента и сохраняет связь между пользователем MAX и аккаунтом студента. Вызывает University API для логина, получает cookies и сохраняет их в БД.",
    response_description="Результат операции логина",
    responses={
        200: {"description": "Логин успешен"},
        400: {"description": "Ошибка валидации или email уже используется другим пользователем"},
        401: {"description": "Неверные credentials студента"},
        404: {"description": "Пользователь или университет не найден"},
        503: {"description": "University API не настроен или endpoint недоступен"}
    }
)
async def login_student(
    request: StudentLoginRequest,
    db: Session = Depends(get_db)
):
    """Выполнить логин студента на сайте университета
    
    Выполняет логин на сайте университета с использованием credentials студента
    и сохраняет связь между пользователем MAX и аккаунтом студента.
    Вызывает University API для логина, получает cookies и сохраняет их в БД.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    - `university_id`: ID университета
    - `student_email`: Email студента для входа на сайт университета
    - `password`: Пароль студента для входа на сайт университета
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8003/api/v1/students/login",
        json={
            "user_id": 123456789,
            "university_id": 1,
            "student_email": "student@university.ru",
            "password": "password123"
        }
    )
    ```
    """
    from repositories.user_repository import UserRepository
    from repositories.university_repository import UniversityRepository
    
    credentials_repo = StudentCredentialsRepository(db)
    user_repo = UserRepository(db)
    university_repo = UniversityRepository(db)
    
    # Проверяем, существует ли университет
    university = university_repo.get_by_id(request.university_id)
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Университет с ID {request.university_id} не найден"
        )
    
    # Проверяем или создаем пользователя
    user = user_repo.get_by_user_id(request.user_id)
    if not user:
        # Создаем пользователя с university_id
        # В реальном приложении здесь должны быть дополнительные данные
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {request.user_id} не найден. Необходимо сначала создать пользователя."
        )
    else:
        # Обновляем university_id пользователя, если он изменился
        if user.university_id != request.university_id:
            user_repo.update(request.user_id, university_id=request.university_id)
    
    # Проверяем конфигурацию и доступность метода для данного университета
    config = await validate_university_api_config(db, request.university_id, "students_login")
    
    # Проверяем уникальность email
    validate_student_email_uniqueness(credentials_repo, request.user_id, request.student_email)
    
    # Проверяем существующую запись
    existing_credential = credentials_repo.get_by_user_id_any(request.user_id)
    
    # Выполняем логин через University API
    login_result = await perform_login(request.student_email, request.password, config)
    
    # Сохраняем или обновляем credentials (только связь user_id <-> student_email)
    # Cookies сохраняются в university-app
    try:
        credential, was_inactive = await save_student_credentials(
            db=db,
            user_id=request.user_id,
            student_email=request.student_email,
            existing_credential=existing_credential if existing_credential and existing_credential.student_email == request.student_email else None
        )
        
        message = "Аккаунт успешно привязан" if was_inactive or not existing_credential else "Сессия обновлена"
        
        return StudentLoginResponse(
            success=True,
            message=message,
            student_email=credential.student_email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении данных: {str(e)}"
        )


@router.get(
    "/students/{user_id}/status",
    response_model=StudentStatusResponse,
    summary="Получить статус студента",
    description="Получает статус связи пользователя с аккаунтом студента. Показывает, связан ли пользователь с аккаунтом студента и когда была создана связь.",
    response_description="Статус связи пользователя с аккаунтом студента",
    responses={
        200: {"description": "Статус успешно получен"}
    }
)
async def get_student_status(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить статус связи пользователя с аккаунтом студента
    
    Возвращает статус связи пользователя MAX с аккаунтом студента.
    Показывает, связан ли пользователь с аккаунтом студента и когда была создана связь.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/students/123456789/status")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    credential = credentials_repo.get_by_user_id(user_id)
    
    if not credential:
        return StudentStatusResponse(
            is_linked=False,
            student_email=None,
            linked_at=None
        )
    
    return StudentStatusResponse(
        is_linked=True,
        student_email=credential.student_email,
        linked_at=credential.created_at
    )


@router.get(
    "/students",
    response_model=list[StudentCredentialsResponse],
    summary="Получить список студентов",
    description="Получает список всех привязанных аккаунтов студентов с пагинацией.",
    response_description="Список привязанных аккаунтов студентов",
    responses={
        200: {"description": "Список студентов успешно получен"}
    }
)
async def get_all_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список всех привязанных аккаунтов студентов
    
    Возвращает список всех привязанных аккаунтов студентов с поддержкой пагинации.
    
    **Параметры:**
    - `skip`: Количество пропускаемых записей (по умолчанию: 0)
    - `limit`: Максимальное количество записей (по умолчанию: 100)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Получить первые 10 студентов
    response = requests.get("http://localhost:8003/api/v1/students?skip=0&limit=10")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    credentials = credentials_repo.get_all(skip=skip, limit=limit)
    return credentials


@router.get(
    "/students/{user_id}",
    response_model=StudentCredentialsResponse,
    summary="Получить credentials студента",
    description="Получает credentials (связь пользователя MAX с аккаунтом студента) по user_id.",
    response_description="Credentials студента",
    responses={
        200: {"description": "Credentials успешно получены"},
        404: {"description": "Связь не найдена"}
    }
)
async def get_student_credentials(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить credentials пользователя по user_id
    
    Возвращает информацию о связи пользователя MAX с аккаунтом студента.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/students/123456789")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    credential = credentials_repo.get_by_user_id(user_id)
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена"
        )
    
    return credential


@router.put(
    "/students/{user_id}",
    response_model=StudentCredentialsResponse,
    summary="Обновить credentials студента",
    description="Обновляет credentials студента (email или выполняет повторный логин с новым паролем). Если указан пароль, выполняется повторный логин на сайте университета.",
    response_description="Обновленные credentials студента",
    responses={
        200: {"description": "Credentials успешно обновлены"},
        404: {"description": "Связь не найдена"},
        401: {"description": "Неверные credentials студента"},
        503: {"description": "University API не настроен или endpoint недоступен"}
    }
)
async def update_student_credentials(
    user_id: int,
    update_data: StudentCredentialsUpdate,
    db: Session = Depends(get_db)
):
    """Обновить credentials студента
    
    Обновляет credentials студента. Можно обновить email или выполнить повторный логин с новым паролем.
    Если указан пароль, выполняется повторный логин на сайте университета.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    - `update_data`: Данные для обновления (email и/или пароль)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Обновить email
    response = requests.put(
        "http://localhost:8003/api/v1/students/123456789",
        json={
            "student_email": "newstudent@university.ru"
        }
    )
    
    # Обновить пароль (выполнить повторный логин)
    response = requests.put(
        "http://localhost:8003/api/v1/students/123456789",
        json={
            "password": "newpassword123"
        }
    )
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена"
        )
    
    # Если обновляется пароль, проверяем конфигурацию и выполняем логин
    # Cookies сохраняются в university-app автоматически при логине
    if update_data.password:
        university_id = get_university_id_from_user(db, user_id)
        config = await validate_university_api_config(db, university_id, "students_login")
        email_to_check = update_data.student_email or credential.student_email
        await perform_login(email_to_check, update_data.password, config)
        
        updated_credential = credentials_repo.update(
            user_id=user_id,
            student_email=update_data.student_email
        )
    else:
        updated_credential = credentials_repo.update(
            user_id=user_id,
            student_email=update_data.student_email
        )
    
    if not updated_credential:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении данных"
        )
    
    return updated_credential


@router.delete(
    "/students/{user_id}/unlink",
    summary="Отвязать студента",
    description="Отвязывает аккаунт студента от пользователя (мягкое удаление). Связь деактивируется, но не удаляется из БД.",
    response_description="Результат отвязки",
    responses={
        200: {"description": "Аккаунт успешно отвязан"},
        404: {"description": "Связь не найдена"}
    }
)
async def unlink_student(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Отвязать аккаунт студента от пользователя
    
    Отвязывает аккаунт студента от пользователя (мягкое удаление).
    Связь деактивируется, но не удаляется из БД. Можно восстановить, выполнив повторный логин.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.delete("http://localhost:8003/api/v1/students/123456789/unlink")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    if not credentials_repo.exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена"
        )
    
    credentials_repo.deactivate(user_id)
    return {"success": True, "message": "Аккаунт успешно отвязан"}


@router.delete(
    "/students/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить credentials студента",
    description="Полностью удаляет связь студента (жесткое удаление). Внимание: это действие необратимо!",
    response_description="Credentials успешно удалены",
    responses={
        204: {"description": "Credentials успешно удалены"},
        404: {"description": "Связь не найдена"}
    }
)
async def delete_student_credentials(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Полностью удалить связь студента
    
    Полностью удаляет связь студента (жесткое удаление).
    Это действие необратимо! Для восстановления необходимо выполнить повторный логин.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.delete("http://localhost:8003/api/v1/students/123456789")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    if not credentials_repo.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена"
        )
    
    return None


@router.get(
    "/students/{user_id}/teachers",
    response_model=TeachersResponse,
    summary="Получить список преподавателей",
    description="Получает список всех преподавателей университета для пользователя. Вызывает University API для получения списка преподавателей.",
    response_description="Список преподавателей с их ID и ФИО",
    responses={
        200: {"description": "Список преподавателей успешно получен"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Связь не найдена (необходимо сначала выполнить логин)"},
        503: {"description": "University API не настроен или endpoint недоступен"}
    }
)
async def get_student_teachers(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить список преподавателей для пользователя
    
    Получает список всех преподавателей университета для пользователя.
    Вызывает University API для получения списка преподавателей.
    Передает student_email в University API, который сам получает cookies из своей БД и парсит данные.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/students/123456789/teachers")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    # Получаем university_id из user_id
    university_id = get_university_id_from_user(db, user_id)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода для университета пользователя
    config = await validate_university_api_config(db, university_id, "students_teachers")
    
    # Вызываем University API для получения списка преподавателей (передаем student_email)
    try:
        result = await call_university_api_tech(credential.student_email, config)
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить список преподавателей"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить список преподавателей")
        )
    
    return TeachersResponse(
        success=True,
        teachers=result.get("teachers"),
        error=None
    )


@router.get(
    "/students/{user_id}/personal_data",
    response_model=PersonalDataResponse,
    summary="Получить данные студента",
    description="Получает структурированные данные студента с личного кабинета университета (ФИО, группа, курс, фото и т.д.). Вызывает University API для получения данных.",
    response_description="Структурированные данные студента",
    responses={
        200: {"description": "Данные студента успешно получены"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Связь не найдена (необходимо сначала выполнить логин)"},
        503: {"description": "University API не настроен или endpoint недоступен"}
    }
)
async def get_student_personal_data(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить данные студента
    
    Получает структурированные данные студента с личного кабинета университета
    (ФИО, группа, курс, фото и т.д.).
    Вызывает University API для получения данных.
    Передает student_email в University API, который сам получает cookies из своей БД и парсит данные.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/students/123456789/personal_data")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    # Получаем university_id из user_id
    university_id = get_university_id_from_user(db, user_id)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода для университета пользователя
    config = await validate_university_api_config(db, university_id, "students_personal_data")
    
    # Вызываем University API для получения personal_data (передаем student_email)
    try:
        result = await call_university_api_personal_data(
            student_email=credential.student_email,
            config=config
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить данные студента"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить данные студента")
        )
    
    return PersonalDataResponse(
        success=True,
        data=result.get("data"),
        error=None
    )


@router.get(
    "/students/{user_id}/teacher/{teacher_id}",
    response_model=TeacherInfoResponse,
    summary="Получить информацию о преподавателе",
    description="Получает информацию о конкретном преподавателе (кафедры, фото). Вызывает University API для получения информации.",
    response_description="Информация о преподавателе (кафедры и фото)",
    responses={
        200: {"description": "Информация о преподавателе успешно получена"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Связь не найдена (необходимо сначала выполнить логин)"},
        503: {"description": "University API не настроен или endpoint недоступен"}
    }
)
async def get_teacher_info(
    user_id: int,
    teacher_id: str,
    db: Session = Depends(get_db)
):
    """Получить информацию о преподавателе
    
    Получает информацию о конкретном преподавателе (кафедры, фото).
    Вызывает University API для получения информации.
    Передает student_email и teacher_id в University API, который сам получает cookies из своей БД и парсит данные.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    - `teacher_id`: ID преподавателя (например, "tech0001")
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/students/123456789/teacher/tech0001")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    # Получаем university_id из user_id
    university_id = get_university_id_from_user(db, user_id)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода для университета пользователя
    config = await validate_university_api_config(db, university_id, "students_teacher_info")
    
    # Вызываем University API для получения информации о преподавателе (передаем student_email и teacher_id)
    try:
        result = await call_university_api_teacher_info(
            student_email=credential.student_email,
            teacher_id=teacher_id,
            config=config
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить информацию о преподавателе"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not result.get("success"):
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


@router.get(
    "/students/{user_id}/schedule",
    response_model=ScheduleResponse,
    summary="Получить расписание студента",
    description="Получает расписание занятий студента за указанный период. Вызывает University API для получения расписания.",
    response_description="Расписание занятий студента",
    responses={
        200: {"description": "Расписание успешно получено"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Связь не найдена (необходимо сначала выполнить логин)"},
        503: {"description": "University API не настроен или endpoint недоступен"}
    }
)
async def get_student_schedule(
    user_id: int,
    date_range: str,
    db: Session = Depends(get_db)
):
    """Получить расписание для пользователя
    
    Получает расписание занятий студента за указанный период.
    Вызывает University API для получения расписания.
    Передает student_email и date_range в University API, который сам получает cookies из своей БД и парсит данные.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    - `date_range`: Промежуток дней в формате ДД.ММ-ДД.ММ (например: 10.11-03.12 или 20.12-05.01) или один день (например: 04.11)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    # Получить расписание за период с 10 ноября по 3 декабря
    response = requests.get("http://localhost:8003/api/v1/students/123456789/schedule?date_range=10.11-03.12")
    
    # Получить расписание за период с переходом на новый год
    response = requests.get("http://localhost:8003/api/v1/students/123456789/schedule?date_range=20.12-05.01")
    ```
    """
    logger.info(f"[SCHEDULE] Начало получения расписания для user_id={user_id}, date_range={date_range}")
    
    credentials_repo = StudentCredentialsRepository(db)
    
    # Получаем university_id из user_id
    logger.info(f"[SCHEDULE] Получаем university_id для user_id={user_id}")
    university_id = get_university_id_from_user(db, user_id)
    logger.info(f"[SCHEDULE] Получен university_id={university_id}")
    
    logger.info(f"[SCHEDULE] Получаем credentials для user_id={user_id}")
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        logger.error(f"[SCHEDULE] Credentials не найдены для user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    logger.info(f"[SCHEDULE] Credentials найдены: student_email={credential.student_email}")
    
    # Проверяем конфигурацию и доступность метода для университета пользователя
    logger.info(f"[SCHEDULE] Проверяем конфигурацию University API для university_id={university_id}")
    config = await validate_university_api_config(db, university_id, "students_schedule")
    logger.info(f"[SCHEDULE] Конфигурация получена: base_url={config.get('base_url')}, endpoint={config.get('endpoints', {}).get('students_schedule')}")
    
    # Вызываем University API для получения расписания (передаем student_email и date_range)
    logger.info(f"[SCHEDULE] Вызываем University API: student_email={credential.student_email}, date_range={date_range}")
    try:
        result = await call_university_api_schedule(
            student_email=credential.student_email,
            date_range=date_range,
            config=config
        )
        logger.info(f"[SCHEDULE] University API вернул результат: success={result.get('success')}, schedule_items={len(result.get('schedule', [])) if result.get('schedule') else 0}")
    except httpx.HTTPStatusError as e:
        logger.error(f"[SCHEDULE] HTTP ошибка от University API: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить расписание"
        )
    except httpx.RequestError as e:
        logger.error(f"[SCHEDULE] Ошибка подключения к University API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not result.get("success"):
        error_msg = result.get("error", "Не удалось получить расписание")
        logger.error(f"[SCHEDULE] University API вернул ошибку: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg
        )
    
    schedule_count = len(result.get("schedule", []))
    logger.info(f"[SCHEDULE] Успешно получено расписание: {schedule_count} занятий")
    
    return ScheduleResponse(
        success=True,
        schedule=result.get("schedule"),
        error=None
    )


@router.get(
    "/students/{user_id}/contacts",
    response_model=ContactsResponse,
    summary="Получить контакты деканатов и кафедр",
    description="Получает контактную информацию деканатов факультетов и кафедр. Вызывает University API для получения контактов.",
    response_description="Контакты деканатов и кафедр",
    responses={
        200: {"description": "Контакты успешно получены"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Связь не найдена (необходимо сначала выполнить логин)"},
        503: {"description": "University API не настроен или endpoint недоступен"}
    }
)
async def get_student_contacts(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить контакты деканатов и кафедр для пользователя
    
    Получает контактную информацию деканатов факультетов и кафедр.
    Вызывает University API для получения контактов.
    Передает student_email в University API, который сам получает cookies из своей БД и парсит данные.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/students/123456789/contacts")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    # Получаем university_id из user_id
    university_id = get_university_id_from_user(db, user_id)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода для университета пользователя
    config = await validate_university_api_config(db, university_id, "students_contacts")
    
    # Вызываем University API для получения контактов (передаем student_email)
    try:
        result = await call_university_api_contacts(
            student_email=credential.student_email,
            config=config
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить контакты"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not result.get("success"):
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
    "/students/{user_id}/platforms",
    response_model=PlatformsResponse,
    summary="Получить список веб-платформ",
    description="Получает список полезных веб-платформ университета для студентов. Вызывает University API для получения списка платформ.",
    response_description="Список полезных веб-платформ",
    responses={
        200: {"description": "Список платформ успешно получен"},
        401: {"description": "Сессия истекла или не найдена"},
        404: {"description": "Связь не найдена (необходимо сначала выполнить логин)"},
        503: {"description": "University API не настроен или endpoint недоступен"}
    }
)
async def get_student_platforms(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить список полезных веб-платформ для пользователя
    
    Получает список полезных веб-платформ университета для студентов.
    Вызывает University API для получения списка платформ.
    Передает запрос в University API, который возвращает статический список платформ.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/students/123456789/platforms")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    # Получаем university_id из user_id
    university_id = get_university_id_from_user(db, user_id)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода для университета пользователя
    config = await validate_university_api_config(db, university_id, "students_platforms")
    
    # Вызываем University API для получения платформ
    try:
        result = await call_university_api_platforms(config=config)
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить платформы"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить платформы")
        )
    
    return PlatformsResponse(
        success=True,
        platforms=result.get("platforms"),
        error=None
    )


@router.get(
    "/students/{user_id}/services",
    response_model=ServicesResponse,
    summary="Получить список сервисов",
    description="Получает список сервисов университета для студентов (не веб-платформы). Вызывает University API для получения списка сервисов.",
    response_description="Список сервисов",
    responses={
        200: {"description": "Список сервисов успешно получен"},
        404: {"description": "Связь не найдена (необходимо сначала выполнить логин)"},
        502: {"description": "Ошибка подключения к University API"}
    }
)
async def get_student_services(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить список сервисов для пользователя
    
    Получает список сервисов университета для студентов (не веб-платформы).
    Вызывает University API для получения списка сервисов.
    Передает запрос в University API, который возвращает статический список сервисов.
    
    **Параметры:**
    - `user_id`: ID пользователя в системе MAX (Telegram user_id)
    
    **Примеры использования:**
    
    ```python
    import requests
    
    response = requests.get("http://localhost:8003/api/v1/students/123456789/services")
    ```
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    # Получаем university_id из user_id
    university_id = get_university_id_from_user(db, user_id)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Получаем конфигурацию University API для университета пользователя
    config = await get_university_config(db, university_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="University API не настроен для данного университета"
        )
    
    # Вызываем University API для получения сервисов
    try:
        result = await call_university_api_services(config=config)
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не удалось получить сервисы"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result.get("error", "Не удалось получить сервисы")
        )
    
    return ServicesResponse(
        success=True,
        services=result.get("services"),
        error=None
    )
