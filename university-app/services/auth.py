"""Модуль для авторизации на сайтах университета"""
import requests
import json
import logging
from typing import Dict, Any
from .base import BaseScraper

logger = logging.getLogger(__name__)


class AuthScraper(BaseScraper):
    """Класс для работы с авторизацией"""
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Выполнить логин на сайте университета (tt.chuvsu.ru)
        
        Отправляет POST запрос напрямую на /auth с данными формы.
        После успешного входа редирект 302 на https://tt.chuvsu.ru/
        
        Returns:
            dict с ключами:
            - success: bool - успешен ли логин
            - session_cookies: str - JSON строка с cookies (если успешно)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        try:
            login_url = f"{self.base_url}/auth"
            
            login_data = {
                "wauto": "1",
                "wname": email,
                "wpass": password,
                "auth": "Войти",
                "pertt": "1",
                "hfac": "0"
            }
            
            response = self.session.post(
                login_url,
                data=login_data,
                allow_redirects=False,
                timeout=10
            )
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                success_url = f"{self.base_url}/"
                
                if location == success_url or location == '/' or success_url in location:
                    cookies_dict = {cookie.name: cookie.value for cookie in self.session.cookies}
                    return {"success": True, "session_cookies": json.dumps(cookies_dict), "error": None}
                else:
                    return {"success": False, "error": "Неверный email или пароль"}
            elif response.status_code == 200:
                if '/auth' in response.url:
                    return {"success": False, "error": "Неверный email или пароль"}
                else:
                    return {"success": False, "error": "Неверный email или пароль"}
            else:
                return {"success": False, "error": f"Ошибка при логине: HTTP {response.status_code}"}
                
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при логине: {e}")
            return {"success": False, "error": f"Ошибка SSL соединения: {str(e)}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при логине: {e}")
            return {"success": False, "error": f"Ошибка подключения к сайту: {str(e)}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при логине: {e}")
            return {"success": False, "error": f"Неожиданная ошибка: {str(e)}"}
    
    def login_lk(self, email: str, password: str) -> Dict[str, Any]:
        """
        Выполнить логин на lk.chuvsu.ru
        
        POST запрос на https://lk.chuvsu.ru/info/login.php с данными:
        - email: email студента
        - password: пароль студента
        - role: "1"
        - enter: ""
        
        При успешном логине: статус 302 Found, редирект на ../student или /student/
        При неуспешном логине: статус 200 OK, остается на https://lk.chuvsu.ru/info/login.php
        
        Args:
            email: Email студента
            password: Пароль студента
        
        Returns:
            dict с ключами:
            - success: bool - успешен ли логин
            - session_cookies: str - JSON строка с cookies (если успешно)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        lk_base_url = "https://lk.chuvsu.ru"
        login_url = f"{lk_base_url}/info/login.php"
        
        # Создаем отдельную сессию для lk.chuvsu.ru
        lk_session = requests.Session()
        lk_session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": lk_base_url,
            "Referer": login_url,
            "Upgrade-Insecure-Requests": "1",
        })
        lk_session.verify = False
        
        try:
            # Сначала получаем страницу логина, чтобы получить начальные cookies (PHPSESSID и т.д.)
            login_page_response = lk_session.get(login_url, timeout=10)
            if login_page_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Не удалось получить страницу логина: HTTP {login_page_response.status_code}"
                }
            
            # Подготавливаем данные формы для POST запроса
            login_data = {
                "email": email,
                "password": password,
                "role": "1",
                "enter": ""
            }
            
            # Отправляем POST запрос на логин без автоматического редиректа
            login_response = lk_session.post(
                login_url,
                data=login_data,
                allow_redirects=False,
                timeout=10
            )
            
            # Проверяем успешность логина по статусу ответа
            if login_response.status_code == 302:
                location = login_response.headers.get('Location', '')
                # Редирект может быть относительным (../student) или абсолютным (/student/)
                if '../student' in location or '/student' in location or 'student/' in location or location.endswith('student') or 'student' in location.lower():
                    cookies_dict = {cookie.name: cookie.value for cookie in lk_session.cookies}
                    logger.info(f"Успешный логин на lk.chuvsu.ru, получены cookies: {list(cookies_dict.keys())}")
                    return {
                        "success": True,
                        "session_cookies": json.dumps(cookies_dict),
                        "error": None
                    }
                else:
                    logger.warning(f"Редирект на неожиданный URL: {location}")
                    return {
                        "success": False,
                        "error": f"Неверный email или пароль для lk.chuvsu.ru (редирект на {location})"
                    }
            elif login_response.status_code == 200:
                final_url = login_response.url
                if 'login.php' in final_url:
                    logger.warning(f"Логин неуспешен, остались на странице логина: {final_url}")
                    return {
                        "success": False,
                        "error": "Неверный email или пароль для lk.chuvsu.ru"
                    }
                else:
                    logger.warning(f"Неожиданный ответ: статус 200, URL: {final_url}")
                    return {
                        "success": False,
                        "error": "Неверный email или пароль для lk.chuvsu.ru"
                    }
            else:
                logger.error(f"Неожиданный статус ответа: {login_response.status_code}")
                return {
                    "success": False,
                    "error": f"Ошибка при логине на lk.chuvsu.ru: HTTP {login_response.status_code}"
                }
                
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при логине на lk.chuvsu.ru: {e}")
            return {
                "success": False,
                "error": f"Ошибка SSL соединения: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при логине на lk.chuvsu.ru: {e}")
            return {
                "success": False,
                "error": f"Ошибка подключения к сайту: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при логине на lk.chuvsu.ru: {e}")
            return {
                "success": False,
                "error": f"Неожиданная ошибка: {str(e)}"
            }
    
    def login_both_sites(self, email: str, password: str) -> Dict[str, Any]:
        """
        Выполнить логин на обоих сайтах: tt.chuvsu.ru и lk.chuvsu.ru
        
        Args:
            email: Email студента
            password: Пароль студента
        
        Returns:
            dict с ключами:
            - success: bool - успешен ли логин на обоих сайтах
            - cookies_by_domain: dict - словарь с cookies по доменам:
              {
                "tt.chuvsu.ru": "{\"cookie1\": \"value1\", ...}",
                "lk.chuvsu.ru": "{\"cookie1\": \"value1\", ...}"
              }
            - error: str - сообщение об ошибке (если неуспешно)
        """
        # Логинимся на tt.chuvsu.ru
        tt_result = self.login(email, password)
        if not tt_result.get("success"):
            return {
                "success": False,
                "cookies_by_domain": {},
                "error": f"Ошибка логина на tt.chuvsu.ru: {tt_result.get('error', 'Unknown error')}"
            }
        
        # Логинимся на lk.chuvsu.ru
        lk_result = self.login_lk(email, password)
        if not lk_result.get("success"):
            logger.error(f"Не удалось залогиниться на lk.chuvsu.ru: {lk_result.get('error')}")
            return {
                "success": False,
                "cookies_by_domain": {
                    "tt.chuvsu.ru": tt_result.get("session_cookies"),
                    "lk.chuvsu.ru": None
                },
                "error": f"Ошибка логина на lk.chuvsu.ru: {lk_result.get('error', 'Unknown error')}"
            }
        
        # Оба логина успешны
        return {
            "success": True,
            "cookies_by_domain": {
                "tt.chuvsu.ru": tt_result.get("session_cookies"),
                "lk.chuvsu.ru": lk_result.get("session_cookies")
            },
            "error": None
        }

