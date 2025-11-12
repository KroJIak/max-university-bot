"""Модуль для работы с преподавателями"""
import requests
import base64
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)


class TeachersScraper(BaseScraper):
    """Класс для работы с преподавателями"""
    
    def get_tech_page(self, cookies_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить список преподавателей со страницы https://tt.chuvsu.ru/index/tech
        
        Парсит HTML страницу и извлекает список преподавателей из формы с id="tt".
        Каждый преподаватель представлен кнопкой вида <button id="tech0000"> с value=ФИО.
        
        Returns:
            dict с ключами:
            - success: bool - успешно ли получены данные
            - teachers: list - список преподавателей (если успешно)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        try:
            if cookies_json:
                self.set_session_cookies(cookies_json)
            
            tech_url = f"{self.base_url}/index/tech"
            
            response = self.session.get(
                tech_url,
                allow_redirects=False,
                timeout=10
            )
            
            if response.status_code == 200:
                if '/index/tech' in response.url or tech_url in response.url:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    form = soup.find('form', {'id': 'tt'})
                    if not form:
                        logger.warning("Форма с id='tt' не найдена на странице")
                        return {"success": False, "teachers": None, "error": "Форма с преподавателями не найдена"}
                    
                    teachers = []
                    buttons = form.find_all('button')
                    logger.debug(f"Найдено всего кнопок в форме: {len(buttons)}")
                    
                    for button in buttons:
                        button_id = button.get('id', '')
                        if button_id and button_id.startswith('tech') and len(button_id) > 4:
                            teacher_name = button.get('value', '').strip()
                            if teacher_name:
                                teachers.append({
                                    "id": button_id,
                                    "name": teacher_name
                                })
                    
                    # Если не нашли через buttons, пробуем через input type="button"
                    if not teachers:
                        logger.warning("Не найдено преподавателей через button, пробуем input")
                        inputs = form.find_all('input', {'type': 'button'})
                        for inp in inputs:
                            inp_id = inp.get('id', '')
                            if inp_id and inp_id.startswith('tech') and len(inp_id) > 4:
                                teacher_name = inp.get('value', '').strip()
                                if teacher_name:
                                    teachers.append({
                                        "id": inp_id,
                                        "name": teacher_name
                                    })
                    
                    logger.info(f"Найдено преподавателей: {len(teachers)}")
                    return {"success": True, "teachers": teachers, "error": None}
                else:
                    return {"success": False, "teachers": None, "error": "Получена неожиданная страница"}
            elif response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if location == '/' or f"{self.base_url}/" in location:
                    return {"success": False, "teachers": None, "error": "Требуется авторизация (редирект на главную)"}
                else:
                    return {"success": False, "teachers": None, "error": f"Неожиданный редирект: {location}"}
            else:
                return {"success": False, "teachers": None, "error": f"Ошибка при получении страницы: HTTP {response.status_code}"}
                
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении страницы tech: {e}")
            return {"success": False, "teachers": None, "error": f"Ошибка SSL соединения: {str(e)}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении страницы tech: {e}")
            return {"success": False, "teachers": None, "error": f"Ошибка подключения к сайту: {str(e)}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении страницы tech: {e}")
            return {"success": False, "teachers": None, "error": f"Неожиданная ошибка: {str(e)}"}
    
    def get_teacher_info(self, teacher_id: str, cookies_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить информацию о преподавателе со страницы https://tt.chuvsu.ru/index/techtt/tech/{teacher_id}
        
        Args:
            teacher_id: ID преподавателя (номер после "tech", например "0000" или "2173")
            cookies_json: JSON строка с cookies от tt.chuvsu.ru (обязательно)
        
        Returns:
            dict с ключами:
            - success: bool - успешно ли получены данные
            - departments: list - список кафедр (если успешно)
            - photo: str - фото в формате base64 data URI (если успешно, иначе None)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        try:
            if cookies_json:
                self.set_session_cookies(cookies_json)
            
            teacher_url = f"{self.base_url}/index/techtt/tech/{teacher_id}"
            
            response = self.session.get(
                teacher_url,
                allow_redirects=False,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Извлекаем кафедры
                departments = []
                htext_span = soup.find('span', {'class': 'htext'})
                if not htext_span:
                    p_tag = soup.find('p')
                    if p_tag:
                        htext_span = p_tag.find('span', {'class': 'htext'})
                
                if htext_span:
                    text_content = htext_span.get_text(separator='\n', strip=True)
                    departments = [dept.strip() for dept in text_content.split('\n') if dept.strip()]
                    logger.info(f"Найдено кафедр для преподавателя {teacher_id}: {len(departments)}")
                
                # Извлекаем фото
                photo_data_url = self._extract_teacher_photo(soup, teacher_id)
                
                return {
                    "success": True,
                    "departments": departments,
                    "photo": photo_data_url,
                    "error": None
                }
            elif response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if location == '/' or f"{self.base_url}/" in location:
                    return {"success": False, "departments": None, "photo": None, "error": "Требуется авторизация (редирект на главную)"}
                else:
                    return {"success": False, "departments": None, "photo": None, "error": f"Неожиданный редирект: {location}"}
            elif response.status_code == 404:
                return {"success": False, "departments": None, "photo": None, "error": f"Преподаватель с ID {teacher_id} не найден"}
            else:
                return {"success": False, "departments": None, "photo": None, "error": f"Ошибка при получении страницы: HTTP {response.status_code}"}
                
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении данных преподавателя: {e}")
            return {"success": False, "departments": None, "photo": None, "error": f"Ошибка SSL соединения: {str(e)}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении данных преподавателя: {e}")
            return {"success": False, "departments": None, "photo": None, "error": f"Ошибка подключения к сайту: {str(e)}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении данных преподавателя: {e}")
            return {"success": False, "departments": None, "photo": None, "error": f"Неожиданная ошибка: {str(e)}"}
    
    def _extract_teacher_photo(self, soup: BeautifulSoup, teacher_id: str) -> Optional[str]:
        """Извлечь фото преподавателя из HTML"""
        photo_data_url = None
        photo_div = soup.find('div', {'id': 'photo'})
        if photo_div:
            photo_img = photo_div.find('img', {'id': 'photosrc'})
            if photo_img:
                photo_src = photo_img.get('src', '')
                if photo_src:
                    # Если относительный URL, делаем абсолютным
                    if photo_src.startswith('http'):
                        photo_url = photo_src
                    elif photo_src.startswith('/'):
                        photo_url = f"{self.base_url}{photo_src}"
                    else:
                        photo_url = f"{self.base_url}/{photo_src}"
                    
                    # Скачиваем изображение используя те же cookies
                    try:
                        photo_response = self.session.get(photo_url, timeout=10)
                        if photo_response.status_code == 200:
                            content_type = photo_response.headers.get('Content-Type', '')
                            if 'image' in content_type:
                                photo_base64 = base64.b64encode(photo_response.content).decode('utf-8')
                                # Определяем формат изображения
                                if 'jpeg' in content_type or 'jpg' in content_type:
                                    photo_mime = 'image/jpeg'
                                elif 'png' in content_type:
                                    photo_mime = 'image/png'
                                elif 'gif' in content_type:
                                    photo_mime = 'image/gif'
                                else:
                                    # Определяем по magic numbers
                                    if photo_response.content[:3] == b'\xff\xd8\xff':
                                        photo_mime = 'image/jpeg'
                                    elif photo_response.content[:8] == b'\x89PNG\r\n\x1a\n':
                                        photo_mime = 'image/png'
                                    elif photo_response.content[:6] in [b'GIF87a', b'GIF89a']:
                                        photo_mime = 'image/gif'
                                    else:
                                        photo_mime = 'image/jpeg'
                                
                                photo_data_url = f"data:{photo_mime};base64,{photo_base64}"
                                logger.info(f"Фото преподавателя {teacher_id} успешно скачано и конвертировано в base64")
                            else:
                                logger.warning(f"Фото для преподавателя {teacher_id} не является изображением. Content-Type: {content_type}")
                        else:
                            logger.warning(f"Не удалось скачать фото для преподавателя {teacher_id}. HTTP {photo_response.status_code}")
                    except Exception as e:
                        logger.error(f"Ошибка при скачивании фото для преподавателя {teacher_id}: {e}")
        
        if not photo_data_url:
            logger.info(f"Фото для преподавателя {teacher_id} не найдено")
        
        return photo_data_url

