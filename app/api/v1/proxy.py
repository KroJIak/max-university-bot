"""Роутеры для работы со студентами"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from repositories.student_credentials_repository import StudentCredentialsRepository
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
    PlatformsResponse
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
    call_university_api_platforms
)
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/students/login", response_model=StudentLoginResponse)
async def login_student(
    request: StudentLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Выполнить логин на сайте университета и сохранить связь с пользователем MAX
    
    Вызывает University API для логина, получает cookies и сохраняет их в БД
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    # Проверяем конфигурацию и доступность метода
    config = await validate_university_api_config(db, "students_login")
    
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


@router.get("/students/{user_id}/status", response_model=StudentStatusResponse)
async def get_student_status(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить статус связи пользователя с аккаунтом студента"""
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


@router.get("/students", response_model=list[StudentCredentialsResponse])
async def get_all_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список всех привязанных аккаунтов студентов"""
    credentials_repo = StudentCredentialsRepository(db)
    credentials = credentials_repo.get_all(skip=skip, limit=limit)
    return credentials


@router.get("/students/{user_id}", response_model=StudentCredentialsResponse)
async def get_student_credentials(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить credentials пользователя по user_id"""
    credentials_repo = StudentCredentialsRepository(db)
    credential = credentials_repo.get_by_user_id(user_id)
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена"
        )
    
    return credential


@router.put("/students/{user_id}", response_model=StudentCredentialsResponse)
async def update_student_credentials(
    user_id: int,
    update_data: StudentCredentialsUpdate,
    db: Session = Depends(get_db)
):
    """Обновить credentials студента"""
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
        config = await validate_university_api_config(db, "students_login")
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


@router.delete("/students/{user_id}/unlink")
async def unlink_student(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Отвязать аккаунт студента от пользователя (мягкое удаление)"""
    credentials_repo = StudentCredentialsRepository(db)
    
    if not credentials_repo.exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена"
        )
    
    credentials_repo.deactivate(user_id)
    return {"success": True, "message": "Аккаунт успешно отвязан"}


@router.delete("/students/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_credentials(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Полностью удалить связь студента (жесткое удаление)"""
    credentials_repo = StudentCredentialsRepository(db)
    
    if not credentials_repo.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена"
        )
    
    return None


@router.get("/students/{user_id}/teachers", response_model=TeachersResponse)
async def get_student_teachers(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить список преподавателей для пользователя
    
    Передает student_email в University API, который сам получает cookies из своей БД и парсит данные
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода
    config = await validate_university_api_config(db, "students_teachers")
    
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


@router.get("/students/{user_id}/personal_data", response_model=PersonalDataResponse)
async def get_student_personal_data(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить данные студента
    
    Передает student_email в University API, который сам получает cookies из своей БД и парсит данные
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода
    config = await validate_university_api_config(db, "students_personal_data")
    
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


@router.get("/students/{user_id}/teacher/{teacher_id}", response_model=TeacherInfoResponse)
async def get_teacher_info(
    user_id: int,
    teacher_id: str,
    db: Session = Depends(get_db)
):
    """
    Получить информацию о преподавателе
    
    Передает student_email и teacher_id в University API, который сам получает cookies из своей БД и парсит данные
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода
    config = await validate_university_api_config(db, "students_teacher_info")
    
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


@router.get("/students/{user_id}/schedule", response_model=ScheduleResponse)
async def get_student_schedule(
    user_id: int,
    week: int = 1,
    db: Session = Depends(get_db)
):
    """
    Получить расписание для пользователя
    
    Args:
        user_id: ID пользователя MAX
        week: Номер недели (1 = текущая неделя, 2 = следующая неделя)
    
    Передает student_email и week в University API, который сам получает cookies из своей БД и парсит данные
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода
    config = await validate_university_api_config(db, "students_schedule")
    
    # Вызываем University API для получения расписания (передаем student_email и week)
    try:
        result = await call_university_api_schedule(
            student_email=credential.student_email,
            week=week,
            config=config
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось получить расписание"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка подключения к University API: {str(e)}"
        )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error", "Не удалось получить расписание")
        )
    
    return ScheduleResponse(
        success=True,
        schedule=result.get("schedule"),
        error=None
    )


@router.get("/students/{user_id}/contacts", response_model=ContactsResponse)
async def get_student_contacts(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить контакты деканатов и кафедр для пользователя
    
    Передает student_email в University API, который сам получает cookies из своей БД и парсит данные
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода
    config = await validate_university_api_config(db, "students_contacts")
    
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


@router.get("/students/{user_id}/platforms", response_model=PlatformsResponse)
async def get_student_platforms(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить список полезных веб-платформ для пользователя
    
    Передает запрос в University API, который возвращает статический список платформ
    """
    credentials_repo = StudentCredentialsRepository(db)
    
    credential = credentials_repo.get_by_user_id(user_id)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена. Необходимо сначала выполнить логин."
        )
    
    # Проверяем конфигурацию и доступность метода
    config = await validate_university_api_config(db, "students_platforms")
    
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
