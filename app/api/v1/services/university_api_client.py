"""Клиент для вызова University API"""
from typing import Dict, Any, Optional
import httpx


async def call_university_api_login(email: str, password: str, config: Dict[str, Any]) -> dict:
    """Вызвать University API для логина
    
    Args:
        email: Email студента
        password: Пароль студента
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
    
    Returns:
        dict с результатом логина от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    base_url = config["base_url"].rstrip("/")
    endpoint = config["endpoints"].get("students_login", "/students/login")
    url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={"student_email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


async def call_university_api_tech(student_email: str, config: Dict[str, Any]) -> dict:
    """Вызвать University API для получения списка преподавателей
    
    Args:
        student_email: Email студента
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
    
    Returns:
        dict со списком преподавателей от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    base_url = config["base_url"].rstrip("/")
    endpoint = config["endpoints"].get("students_teachers", "/students/teachers")
    url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={"student_email": student_email},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


async def call_university_api_personal_data(
    student_email: str,
    config: Dict[str, Any]
) -> dict:
    """Вызвать University API для получения данных студента
    
    Args:
        student_email: Email студента
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
    
    Returns:
        dict с HTML содержимым страницы personal_data от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    base_url = config["base_url"].rstrip("/")
    endpoint = config["endpoints"].get("students_personal_data", "/students/personal_data")
    url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={"student_email": student_email},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


async def call_university_api_teacher_info(
    student_email: str,
    teacher_id: str,
    config: Dict[str, Any]
) -> dict:
    """Вызвать University API для получения информации о преподавателе
    
    Args:
        student_email: Email студента
        teacher_id: ID преподавателя (номер после "tech", например "0000" или "2173")
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
    
    Returns:
        dict с информацией о преподавателе от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    base_url = config["base_url"].rstrip("/")
    endpoint = config["endpoints"].get("students_teacher_info", "/students/teacher_info")
    url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={"student_email": student_email, "teacher_id": teacher_id},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


async def call_university_api_schedule(
    student_email: str,
    week: int,
    config: Dict[str, Any]
) -> dict:
    """Вызвать University API для получения расписания
    
    Args:
        student_email: Email студента
        week: Номер недели (1 = текущая неделя, 2 = следующая неделя)
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
    
    Returns:
        dict с расписанием от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    base_url = config["base_url"].rstrip("/")
    endpoint = config["endpoints"].get("students_schedule", "/students/schedule")
    url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={"student_email": student_email, "week": week},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


async def call_university_api_contacts(
    student_email: str,
    config: Dict[str, Any]
) -> dict:
    """Вызвать University API для получения контактов деканатов и кафедр
    
    Args:
        student_email: Email студента
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
    
    Returns:
        dict с контактами от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    base_url = config["base_url"].rstrip("/")
    endpoint = config["endpoints"].get("students_contacts", "/students/contacts")
    url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={"student_email": student_email},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()


async def call_university_api_platforms(
    config: Dict[str, Any]
) -> dict:
    """Вызвать University API для получения списка полезных веб-платформ
    
    Args:
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
    
    Returns:
        dict со списком платформ от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    base_url = config["base_url"].rstrip("/")
    endpoint = config["endpoints"].get("students_platforms", "/students/platforms")
    url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            url,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

