"""Базовый класс для скрапера"""
import requests
import json
import logging
import urllib3

# Отключаем предупреждения о небезопасных SSL запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class BaseScraper:
    """Базовый класс для работы с сайтами университета"""
    
    def __init__(self):
        self.base_url = "https://tt.chuvsu.ru"
        self.lk_base_url = "https://lk.chuvsu.ru"
        self.session = requests.Session()
        # Устанавливаем заголовки для имитации браузера
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        })
        # Отключаем проверку SSL сертификата
        self.session.verify = False
    
    def get_session_cookies(self) -> dict:
        """Получить текущие cookies сессии"""
        return {cookie.name: cookie.value for cookie in self.session.cookies}
    
    def set_session_cookies(self, cookies_json: str):
        """Восстановить сессию из сохраненных cookies"""
        try:
            cookies_dict = json.loads(cookies_json)
            for name, value in cookies_dict.items():
                self.session.cookies.set(name, value)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Ошибка при восстановлении cookies: {e}")

