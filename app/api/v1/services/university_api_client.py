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
    import logging
    logger = logging.getLogger(__name__)
    
    base_url = config["base_url"].rstrip("/")
    endpoints = config.get("endpoints", {})
    
    # Получаем endpoint из конфигурации (должен быть проверен в validate_university_api_config)
    endpoint = endpoints.get("students_login")
    
    if not endpoint or endpoint.strip() == "":
        raise ValueError("Endpoint 'students_login' не настроен в конфигурации")
    
    logger.info(f"Используем endpoint из конфигурации: {endpoint}")
    print(f"[DEBUG] Используем endpoint из конфигурации: {endpoint}")
    
    # Убеждаемся, что endpoint начинается с "/"
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    url = f"{base_url}{endpoint}"
    logger.info(f"Calling University API login: {url}")
    print(f"[DEBUG] Calling University API login: {url}")  # Для отладки
    print(f"[DEBUG] base_url: {base_url}, endpoint: {endpoint}, full_url: {url}")  # Для отладки
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                url,
                json={"student_email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            logger.info(f"University API login response: {response.status_code}")
            print(f"[DEBUG] University API login response: {response.status_code}")  # Для отладки
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            print(f"[DEBUG] HTTP error: {e.response.status_code} - {e.response.text}")  # Для отладки
            raise


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
    date_range: str,
    config: Dict[str, Any]
) -> dict:
    """Вызвать University API для получения расписания
    
    Args:
        student_email: Email студента
        date_range: Промежуток дней в формате ДД.ММ-ДД.ММ (например: 10.11-03.12 или 20.12-05.01)
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
    
    Returns:
        dict с расписанием от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[UNIVERSITY_API_CLIENT] Начало вызова University API для расписания: student_email={student_email}, date_range={date_range}")
    
    base_url = config["base_url"].rstrip("/")
    endpoints = config.get("endpoints", {})
    endpoint = endpoints.get("students_schedule")
    
    if not endpoint or endpoint.strip() == "":
        logger.error(f"[UNIVERSITY_API_CLIENT] Endpoint 'students_schedule' не настроен в конфигурации")
        raise ValueError("Endpoint 'students_schedule' не настроен в конфигурации")
    
    logger.info(f"[UNIVERSITY_API_CLIENT] Используем endpoint: {endpoint}")
    
    # Убеждаемся, что endpoint начинается с "/"
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    url = f"{base_url}{endpoint}"
    logger.info(f"[UNIVERSITY_API_CLIENT] Полный URL: {url}")
    print(f"[DEBUG] [UNIVERSITY_API_CLIENT] Вызов University API: {url}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"[UNIVERSITY_API_CLIENT] Отправка POST запроса: {url}")
            response = await client.post(
                url,
                json={"student_email": student_email, "date_range": date_range},
                headers={"Content-Type": "application/json"}
            )
            logger.info(f"[UNIVERSITY_API_CLIENT] Получен ответ: status_code={response.status_code}")
            print(f"[DEBUG] [UNIVERSITY_API_CLIENT] Ответ: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            logger.info(f"[UNIVERSITY_API_CLIENT] Ответ успешно распарсен: success={result.get('success')}")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"[UNIVERSITY_API_CLIENT] HTTP ошибка: {e.response.status_code} - {e.response.text}")
            print(f"[DEBUG] [UNIVERSITY_API_CLIENT] HTTP ошибка: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"[UNIVERSITY_API_CLIENT] Неожиданная ошибка: {str(e)}")
            print(f"[DEBUG] [UNIVERSITY_API_CLIENT] Неожиданная ошибка: {str(e)}")
            raise


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


async def call_university_api_services(
    config: Dict[str, Any]
) -> dict:
    """Вызвать University API для получения списка сервисов
    
    Args:
        config: Конфигурация University API из БД (должен содержать base_url)
    
    Returns:
        dict со списком сервисов от University API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    base_url = config["base_url"].rstrip("/")
    url = f"{base_url}/students/services"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            url,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

