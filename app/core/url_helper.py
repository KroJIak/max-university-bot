import os
from typing import Optional
import httpx


async def get_url_with_fallback(local_url: str, cloudpub_url: Optional[str] = None) -> str:
    """
    Получить URL с fallback на CLOUDPUB_URL если локальный запрос не работает
    
    Проверяет доступность локального URL через GET запрос на health endpoint.
    Если локальный URL недоступен, возвращает cloudpub URL.
    
    Args:
        local_url: Локальный URL для попытки подключения
        cloudpub_url: CLOUDPUB_URL из переменной окружения (опционально)
    
    Returns:
        URL который работает (локальный или cloudpub)
    """
    # Если cloudpub_url не передан, пытаемся получить из переменной окружения
    if not cloudpub_url:
        cloudpub_url = os.getenv("UNIVERSITY_API_CLOUDPUB_URL") or os.getenv("MAX_API_CLOUDPUB_URL")
    
    # Если cloudpub_url не задан, просто возвращаем локальный URL
    if not cloudpub_url:
        return local_url
    
    # Пробуем сначала локальный URL через health endpoint
    # Извлекаем base_url из local_url и проверяем /health
    from urllib.parse import urlparse, urlunparse
    local_parsed = urlparse(local_url)
    health_url = urlunparse((
        local_parsed.scheme,
        local_parsed.netloc,
        "/health",  # Проверяем health endpoint
        "",
        "",
        ""
    ))
    
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Делаем GET запрос на health endpoint для проверки доступности
            response = await client.get(health_url)
            if response.status_code < 500:  # Если не 5xx ошибка, считаем что работает
                return local_url
    except (httpx.RequestError, httpx.TimeoutException):
        # Локальный URL не доступен, используем cloudpub
        pass
    
    # Если локальный не работает, используем cloudpub
    # Заменяем хост и порт в local_url на cloudpub_url
    if cloudpub_url:
        cloudpub_parsed = urlparse(cloudpub_url.rstrip("/"))
        
        # Собираем новый URL с cloudpub хостом, но с путем из local_url
        new_url = urlunparse((
            cloudpub_parsed.scheme or "http",
            cloudpub_parsed.netloc,
            local_parsed.path,
            local_parsed.params,
            local_parsed.query,
            local_parsed.fragment
        ))
        return new_url
    
    return local_url

