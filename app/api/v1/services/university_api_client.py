"""Клиент для вызова University API"""
from typing import Dict, Any, Optional
import httpx
import os
import logging

logger = logging.getLogger(__name__)


def get_ghost_api_urls() -> tuple[Optional[str], str]:
    """Получить URL Ghost API из переменных окружения (primary и fallback)
    
    Returns:
        tuple: (primary_url, fallback_url) - primary (domain) и fallback (host:port)
    """
    domain_url = os.getenv("GHOST_API_DOMAIN_URL", "").strip()
    host = os.getenv("GHOST_API_HOST", "ghost-api").strip()
    port = os.getenv("GHOST_API_PORT", "8004").strip()
    
    primary_url = domain_url.rstrip("/") if domain_url else None
    fallback_url = f"http://{host}:{port}"
    
    return (primary_url, fallback_url)


def get_university_api_urls(base_url: str) -> tuple[Optional[str], str]:
    """Получить URL University API с fallback (primary и fallback)
    
    Args:
        base_url: Base URL из конфигурации (может быть domain или host:port)
    
    Returns:
        tuple: (primary_url, fallback_url) - primary (domain) и fallback (host:port)
    """
    base_url = base_url.rstrip("/")
    
    # Получаем fallback из переменных окружения
    host = os.getenv("UNIVERSITY_API_HOST", "university-api").strip()
    port = os.getenv("UNIVERSITY_API_PORT", "8001").strip()
    fallback_url = f"http://{host}:{port}"
    
    # Если base_url начинается с http:// или https://, это может быть domain
    if base_url.startswith("http://") or base_url.startswith("https://"):
        # Извлекаем хост из URL
        parsed = base_url.replace("http://", "").replace("https://", "").split("/")[0]
        
        # Проверяем, является ли это доменом (не localhost, не IP, не содержит :port)
        if ":" in parsed:
            # Есть порт в URL - это host:port, не domain
            primary_url = None
            return (primary_url, base_url)
        elif parsed in ["localhost", "127.0.0.1", "0.0.0.0"] or parsed.replace(".", "").isdigit():
            # Это localhost или IP - не domain
            primary_url = None
            return (primary_url, base_url)
        else:
            # Это домен - используем как primary
            primary_url = base_url
            return (primary_url, fallback_url)
    else:
        # Это уже host:port без протокола
        primary_url = None
        fallback_url = f"http://{base_url}" if not base_url.startswith("http") else base_url
        return (primary_url, fallback_url)


def get_ghost_api_standard_endpoint(endpoint_key: str) -> str:
    """Получить стандартный endpoint Ghost API для ключа endpoint
    
    Args:
        endpoint_key: Ключ endpoint (например, "students_teachers")
    
    Returns:
        Стандартный endpoint Ghost API
    """
    # Маппинг ключей на стандартные endpoints Ghost API
    endpoint_mapping = {
        "students_teachers": "/students/teachers",
        "students_schedule": "/students/schedule",
        "students_personal_data": "/students/personal_data",
        "students_contacts": "/students/contacts",
        "students_platforms": "/students/platforms",
        "students_maps": "/students/maps",
        "students_teacher_info": "/students/teacher_info",
    }
    return endpoint_mapping.get(endpoint_key, f"/students/{endpoint_key.replace('students_', '')}")


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
    
    # Используем University API с fallback
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    logger.info(f"Calling University API login: primary={primary_full_url}, fallback={fallback_full_url}")
    print(f"[DEBUG] Calling University API login: primary={primary_full_url}, fallback={fallback_full_url}")
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="POST",
        json_data={"student_email": email, "password": password},
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )


async def _make_request_with_fallback(
    primary_url: Optional[str],
    fallback_url: str,
    method: str = "POST",
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    service_name: str = "API"
) -> dict:
    """Универсальная функция для выполнения HTTP запроса с fallback логикой
    
    Сначала пытается выполнить запрос по primary_url (domain), если не получается,
    пробует fallback_url (host:port).
    
    Args:
        primary_url: Основной URL (domain), может быть None
        fallback_url: Fallback URL (host:port)
        method: HTTP метод (GET или POST)
        json_data: JSON данные для POST запроса
        headers: HTTP заголовки
        service_name: Имя сервиса для логирования
    
    Returns:
        dict с ответом от API
    
    Raises:
        httpx.HTTPStatusError: Если оба URL вернули ошибку HTTP
        httpx.RequestError: Если оба URL недоступны
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    # Список URL для попыток (primary, затем fallback)
    urls_to_try = []
    if primary_url:
        urls_to_try.append(primary_url)
    urls_to_try.append(fallback_url)
    
    last_error = None
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for url in urls_to_try:
            try:
                logger.info(f"Calling {service_name}: {url} (method: {method})")
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    response = await client.post(url, json=json_data or {}, headers=headers)
                response.raise_for_status()
                logger.info(f"{service_name} успешно ответил: {url}")
                return response.json()
            except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as e:
                last_error = e
                logger.warning(f"{service_name} недоступен по {url}: {type(e).__name__}, пробуем следующий URL...")
                continue
        
        # Если все URL не сработали, выбрасываем последнюю ошибку
        if isinstance(last_error, httpx.HTTPStatusError):
            raise last_error
        elif isinstance(last_error, httpx.RequestError):
            raise httpx.RequestError(
                f"{service_name} недоступен по всем URL: {', '.join(urls_to_try)}",
                request=last_error.request if hasattr(last_error, 'request') else None
            )
        else:
            raise httpx.RequestError(f"{service_name} недоступен по всем URL: {', '.join(urls_to_try)}")


async def call_ghost_api(
    endpoint_key: str,
    method: str = "POST",
    json_data: Optional[Dict[str, Any]] = None,
    university_id: int = None
) -> dict:
    """Вызвать Ghost API по стандартному endpoint с fallback на host:port
    
    Args:
        endpoint_key: Ключ endpoint (например, "students_teachers")
        method: HTTP метод (GET или POST)
        json_data: JSON данные для POST запроса
        university_id: ID университета (для заголовка X-University-Id)
    
    Returns:
        dict с ответом от Ghost API
    
    Raises:
        httpx.HTTPStatusError: Если оба URL вернули ошибку HTTP
        httpx.RequestError: Если оба URL недоступны
    """
    primary_url, fallback_url = get_ghost_api_urls()
    endpoint = get_ghost_api_standard_endpoint(endpoint_key)
    
    headers = {"Content-Type": "application/json"}
    if university_id:
        headers["X-University-Id"] = str(university_id)
    
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method=method,
        json_data=json_data,
        headers=headers,
        service_name="Ghost API"
    )


async def call_university_api_tech(student_email: str, config: Dict[str, Any], university_id: int = None) -> dict:
    """Вызвать University API или Ghost API для получения списка преподавателей
    
    Args:
        student_email: Email студента
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
        university_id: ID университета (для Ghost API)
    
    Returns:
        dict со списком преподавателей от University API или Ghost API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    # Если нужно использовать ghost-api
    if config.get("use_ghost_api", False):
        return await call_ghost_api(
            "students_teachers",
            method="POST",
            json_data={"student_email": student_email},
            university_id=university_id
        )
    
    # Используем University API с fallback
    base_url = config["base_url"]
    endpoint = config["endpoints"].get("students_teachers", "/students/teachers")
    
    # Убеждаемся, что endpoint начинается с "/"
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="POST",
        json_data={"student_email": student_email},
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )


async def call_university_api_personal_data(
    student_email: str,
    config: Dict[str, Any],
    university_id: int = None
) -> dict:
    """Вызвать University API или Ghost API для получения данных студента
    
    Args:
        student_email: Email студента
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
        university_id: ID университета (для Ghost API)
    
    Returns:
        dict с данными студента от University API или Ghost API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    # Если нужно использовать ghost-api
    if config.get("use_ghost_api", False):
        return await call_ghost_api(
            "students_personal_data",
            method="POST",
            json_data={"student_email": student_email},
            university_id=university_id
        )
    
    # Используем University API с fallback
    base_url = config["base_url"]
    endpoint = config["endpoints"].get("students_personal_data", "/students/personal_data")
    
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="POST",
        json_data={"student_email": student_email},
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )


async def call_university_api_teacher_info(
    student_email: str,
    teacher_id: str,
    config: Dict[str, Any],
    university_id: int = None
) -> dict:
    """Вызвать University API или Ghost API для получения информации о преподавателе
    
    Args:
        student_email: Email студента
        teacher_id: ID преподавателя (номер после "tech", например "0000" или "2173")
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
        university_id: ID университета (для Ghost API)
    
    Returns:
        dict с информацией о преподавателе от University API или Ghost API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    # Если нужно использовать ghost-api
    if config.get("use_ghost_api", False):
        return await call_ghost_api(
            "students_teacher_info",
            method="POST",
            json_data={"student_email": student_email, "teacher_id": teacher_id},
            university_id=university_id
        )
    
    # Используем University API с fallback
    base_url = config["base_url"]
    endpoint = config["endpoints"].get("students_teacher_info", "/students/teacher_info")
    
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="POST",
        json_data={"student_email": student_email, "teacher_id": teacher_id},
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )


async def call_university_api_schedule(
    student_email: str,
    date_range: str,
    config: Dict[str, Any],
    university_id: int = None
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
    
    # Если нужно использовать ghost-api
    if config.get("use_ghost_api", False):
        # Ghost API использует формат week (int) вместо date_range (string)
        # Пока используем week=1 (текущая неделя) как значение по умолчанию
        # TODO: Преобразовать date_range в week при необходимости
        try:
            # Пытаемся преобразовать date_range в week (пока используем 1)
            week = 1  # По умолчанию текущая неделя
        except:
            week = 1
        return await call_ghost_api(
            "students_schedule",
            method="POST",
            json_data={"student_email": student_email, "week": week},
            university_id=university_id
        )
    
    logger.info(f"[UNIVERSITY_API_CLIENT] Начало вызова University API для расписания: student_email={student_email}, date_range={date_range}")
    
    base_url = config["base_url"]
    endpoints = config.get("endpoints", {})
    endpoint = endpoints.get("students_schedule")
    
    if not endpoint or endpoint.strip() == "":
        logger.error(f"[UNIVERSITY_API_CLIENT] Endpoint 'students_schedule' не настроен в конфигурации")
        raise ValueError("Endpoint 'students_schedule' не настроен в конфигурации")
    
    logger.info(f"[UNIVERSITY_API_CLIENT] Используем endpoint: {endpoint}")
    
    # Убеждаемся, что endpoint начинается с "/"
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    # Используем University API с fallback
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="POST",
        json_data={"student_email": student_email, "date_range": date_range},
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )


async def call_university_api_contacts(
    student_email: str,
    config: Dict[str, Any],
    university_id: int = None
) -> dict:
    """Вызвать University API или Ghost API для получения контактов деканатов и кафедр
    
    Args:
        student_email: Email студента
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
        university_id: ID университета (для Ghost API)
    
    Returns:
        dict с контактами от University API или Ghost API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    # Если нужно использовать ghost-api
    if config.get("use_ghost_api", False):
        return await call_ghost_api(
            "students_contacts",
            method="POST",
            json_data={"student_email": student_email},
            university_id=university_id
        )
    
    # Используем University API с fallback
    base_url = config["base_url"]
    endpoint = config["endpoints"].get("students_contacts", "/students/contacts")
    
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="POST",
        json_data={"student_email": student_email},
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )


async def call_university_api_platforms(
    config: Dict[str, Any],
    university_id: int = None
) -> dict:
    """Вызвать University API или Ghost API для получения списка полезных веб-платформ
    
    Args:
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
        university_id: ID университета (для Ghost API)
    
    Returns:
        dict со списком платформ от University API или Ghost API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    # Если нужно использовать ghost-api
    if config.get("use_ghost_api", False):
        return await call_ghost_api(
            "students_platforms",
            method="GET",
            university_id=university_id
        )
    
    # Используем University API с fallback
    base_url = config["base_url"]
    endpoint = config["endpoints"].get("students_platforms", "/students/platforms")
    
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="GET",
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )


async def call_university_api_maps(
    config: Dict[str, Any],
    university_id: int = None
) -> dict:
    """Вызвать University API или Ghost API для получения списка карт корпусов
    
    Args:
        config: Конфигурация University API из БД (должен содержать base_url и endpoints)
        university_id: ID университета (для Ghost API)
    
    Returns:
        dict со списком карт от University API или Ghost API
    
    Raises:
        httpx.HTTPStatusError: Если запрос вернул ошибку HTTP
        httpx.RequestError: Если произошла ошибка подключения
    """
    # Если нужно использовать ghost-api
    if config.get("use_ghost_api", False):
        return await call_ghost_api(
            "students_maps",
            method="GET",
            university_id=university_id
        )
    
    # Используем University API с fallback
    base_url = config["base_url"]
    endpoint = config["endpoints"].get("students_maps", "/students/maps")
    
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="GET",
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )


async def call_university_api_services(
    config: Dict[str, Any],
    university_id: int = None
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
    # Используем University API с fallback
    base_url = config["base_url"]
    endpoint = "/students/services"
    
    primary_url, fallback_url = get_university_api_urls(base_url)
    primary_full_url = f"{primary_url}{endpoint}" if primary_url else None
    fallback_full_url = f"{fallback_url}{endpoint}"
    
    return await _make_request_with_fallback(
        primary_url=primary_full_url,
        fallback_url=fallback_full_url,
        method="GET",
        headers={"Content-Type": "application/json"},
        service_name="University API"
    )

