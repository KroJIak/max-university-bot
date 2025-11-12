"""Модуль для работы с личными данными студента"""
import requests
import json
import base64
import re
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)


class PersonalDataScraper(BaseScraper):
    """Класс для работы с личными данными студента"""
    
    def get_student_personal_data(
        self, 
        cookies_json: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Получить данные студента с https://lk.chuvsu.ru/student/personal_data.php
        
        Args:
            cookies_json: JSON строка с cookies от lk.chuvsu.ru (обязательно)
        
        Returns:
            dict с ключами:
            - success: bool - успешно ли получены данные
            - data: dict - структурированные данные студента (если успешно)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        if not cookies_json:
            return {
                "success": False,
                "data": None,
                "error": "Требуются cookies сессии от lk.chuvsu.ru"
            }
        
        lk_base_url = "https://lk.chuvsu.ru"
        personal_data_url = f"{lk_base_url}/student/personal_data.php"
        
        lk_session = requests.Session()
        lk_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        })
        lk_session.verify = False
        
        try:
            cookies_dict = json.loads(cookies_json)
            for name, value in cookies_dict.items():
                lk_session.cookies.set(name, value, domain='.chuvsu.ru')
                lk_session.cookies.set(name, value)
            
            response = lk_session.get(
                personal_data_url,
                allow_redirects=False,
                timeout=10
            )
            
            if response.status_code == 200 and 'personal_data.php' in response.url:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                def extract_from_javascript(field_name: str) -> Optional[str]:
                    patterns = [
                        rf"document\.form_personal_data\.{field_name}\.value\s*=\s*['\"]([^'\"]+)['\"]",
                        rf"document\.getElementById\s*\(\s*['\"]id_{field_name}['\"]\s*\)\.value\s*=\s*['\"]([^'\"]+)['\"]",
                    ]
                    
                    for script in soup.find_all('script'):
                        if not script.string:
                            continue
                        script_text = script.string
                        for pattern in patterns:
                            match = re.search(pattern, script_text, re.IGNORECASE)
                            if match:
                                value = match.group(1)
                                return value.strip() or None
                    return None
                
                def get_input_value(field_id: str, field_name: str = None) -> Optional[str]:
                    if field_name:
                        js_value = extract_from_javascript(field_name)
                        if js_value:
                            return js_value
                    
                    input_field = soup.find('input', {'id': field_id})
                    if input_field:
                        value = input_field.get('value', '')
                        if value:
                            return value.strip() or None
                    return None
                
                field_mapping = {
                    "id_fam": "fam",
                    "id_nam": "nam",
                    "id_oth": "oth",
                    "id_sex": "sex",
                    "id_birthday": "birthday",
                    "id_zachetka": "zachetka",
                    "id_faculty": "faculty",
                    "id_spec": "spec",
                    "id_profile": "profile",
                    "id_groupname": "groupname",
                    "id_course": "course",
                    "id_phone": "phone",
                }
                
                data = {}
                for field_id, field_name in field_mapping.items():
                    value = get_input_value(field_id, field_name)
                    key = field_id.replace("id_", "")
                    if key == "nam":
                        key = "name"
                    elif key == "oth":
                        key = "patronymic"
                    elif key == "groupname":
                        key = "group"
                    data[key] = value
                
                # Извлекаем фото
                photo_img = soup.find('img', {'id': 'id_face'})
                if photo_img:
                    photo_src = photo_img.get('src', '')
                    if photo_src:
                        if photo_src.startswith('http'):
                            photo_url = photo_src
                        elif photo_src.startswith('/'):
                            photo_url = f"{lk_base_url}{photo_src}"
                        else:
                            photo_url = f"{lk_base_url}/student/{photo_src}"
                        
                        try:
                            photo_response = lk_session.get(photo_url, timeout=10)
                            if photo_response.status_code == 200:
                                content_type = photo_response.headers.get('Content-Type', '')
                                if 'image' in content_type:
                                    photo_base64 = base64.b64encode(photo_response.content).decode('utf-8')
                                    if 'jpeg' in content_type or 'jpg' in content_type:
                                        photo_data_url = f"data:image/jpeg;base64,{photo_base64}"
                                    elif 'png' in content_type:
                                        photo_data_url = f"data:image/png;base64,{photo_base64}"
                                    elif 'gif' in content_type:
                                        photo_data_url = f"data:image/gif;base64,{photo_base64}"
                                    else:
                                        if photo_response.content[:3] == b'\xff\xd8\xff':
                                            photo_data_url = f"data:image/jpeg;base64,{photo_base64}"
                                        elif photo_response.content[:8] == b'\x89PNG\r\n\x1a\n':
                                            photo_data_url = f"data:image/png;base64,{photo_base64}"
                                        else:
                                            photo_data_url = f"data:image/jpeg;base64,{photo_base64}"
                                    
                                    data["photo"] = photo_data_url
                                    logger.info(f"Фото успешно скачано и конвертировано в base64")
                                else:
                                    data["photo"] = None
                            else:
                                data["photo"] = None
                        except Exception as e:
                            logger.error(f"Ошибка при скачивании фото: {e}")
                            data["photo"] = None
                    else:
                        data["photo"] = None
                else:
                    data["photo"] = None
                
                filled_fields = {k: v for k, v in data.items() if v is not None}
                logger.info(f"Успешно извлечены данные студента: {len(filled_fields)}/{len(data)} полей заполнено")
                
                return {
                    "success": True,
                    "data": data,
                    "error": None
                }
            elif response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if 'login.php' in location:
                    return {
                        "success": False,
                        "data": None,
                        "error": "Cookies недействительны. Требуется повторный логин."
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "error": f"Неожиданный редирект: {location}"
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Ошибка при получении страницы: HTTP {response.status_code}"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при парсинге cookies: {e}")
            return {
                "success": False,
                "data": None,
                "error": f"Неверный формат cookies: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге HTML: {e}")
            return {
                "success": False,
                "data": None,
                "error": f"Ошибка при парсинге данных: {str(e)}"
            }
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении данных студента: {e}")
            return {
                "success": False,
                "data": None,
                "error": f"Ошибка SSL соединения: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении данных студента: {e}")
            return {
                "success": False,
                "data": None,
                "error": f"Ошибка подключения к сайту: {str(e)}"
            }
