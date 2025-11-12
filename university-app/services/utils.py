"""Утилиты для работы скрапера"""
import logging

logger = logging.getLogger(__name__)

# Словарь для преобразования русских названий месяцев в числа
MONTHS_RU = {
    'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
    'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
}


def parse_date_to_dd_mm_yyyy(date_str: str) -> str:
    """
    Преобразует дату из формата "10 ноября 2025, Понедельник" в "10.11.2025"
    
    Args:
        date_str: Дата в формате "10 ноября 2025, Понедельник" или "10 ноября 2025"
    
    Returns:
        Дата в формате "10.11.2025" или исходная строка, если не удалось распарсить
    """
    try:
        # Убираем день недели (всё после запятой)
        date_part = date_str.split(',')[0].strip()
        
        # Парсим дату: "10 ноября 2025"
        parts = date_part.split()
        if len(parts) == 3:
            day = int(parts[0])
            month_name = parts[1].lower()
            year = int(parts[2])
            
            # Получаем номер месяца
            month = MONTHS_RU.get(month_name)
            if month:
                return f"{day:02d}.{month:02d}.{year}"
        
        # Если не удалось распарсить, возвращаем исходную строку
        logger.warning(f"Не удалось распарсить дату: {date_str}")
        return date_str
    except Exception as e:
        logger.error(f"Ошибка при парсинге даты '{date_str}': {e}")
        return date_str

