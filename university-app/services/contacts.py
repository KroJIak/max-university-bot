"""Модуль для работы с контактами"""
import requests
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)


class ContactsScraper(BaseScraper):
    """Класс для работы с контактами деканатов и кафедр"""
    
    def get_contacts(self, cookies_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить контакты деканатов и кафедр со страницы https://lk.chuvsu.ru/student/contacts.php
        
        Args:
            cookies_json: JSON строка с cookies от lk.chuvsu.ru (обязательно)
        
        Returns:
            dict с ключами:
            - success: bool - успешно ли получены данные
            - deans: list - список деканатов (если успешно)
            - departments: list - список кафедр (если успешно)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        try:
            if cookies_json:
                self.set_session_cookies(cookies_json)
            
            contacts_url = f"{self.lk_base_url}/student/contacts.php"
            
            response = self.session.get(
                contacts_url,
                allow_redirects=False,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                deans = []
                departments = []
                
                # Парсим деканаты из <div id="tabs_XXXXX-1">
                all_divs = soup.find_all('div', id=True)
                deans_div = None
                for div in all_divs:
                    div_id = div.get('id', '')
                    if div_id.endswith('-1') and 'tabs' in div_id.lower():
                        deans_div = div
                        break
                
                if deans_div:
                    deans_table = deans_div.find('table')
                    if deans_table:
                        deans_rows = deans_table.find_all('tr')
                        for row in deans_rows:
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                faculty_cell = cells[0]
                                phone_cell = cells[1]
                                email_cell = cells[2]
                                
                                faculty = faculty_cell.get_text(strip=True) if faculty_cell else None
                                phone = phone_cell.get_text(strip=True) if phone_cell else None
                                
                                email = None
                                email_link = email_cell.find('a') if email_cell else None
                                if email_link:
                                    href = email_link.get('href', '')
                                    if href.startswith('mailto:'):
                                        email = href.replace('mailto:', '').strip()
                                    else:
                                        email = email_link.get_text(strip=True)
                                elif email_cell:
                                    email = email_cell.get_text(strip=True)
                                
                                if faculty:
                                    deans.append({
                                        "faculty": faculty,
                                        "phone": phone if phone else None,
                                        "email": email if email else None
                                    })
                
                # Парсим кафедры из <div id="tabs_XXXXX-2">
                departments_div = None
                for div in all_divs:
                    div_id = div.get('id', '')
                    if div_id.endswith('-2') and 'tabs' in div_id.lower():
                        departments_div = div
                        break
                
                if departments_div:
                    departments_table = departments_div.find('table')
                    if departments_table:
                        departments_rows = departments_table.find_all('tr')
                        for row in departments_rows:
                            cells = row.find_all('td')
                            if len(cells) >= 4:
                                faculty_cell = cells[0]
                                department_cell = cells[1]
                                phones_cell = cells[2]
                                email_cell = cells[3]
                                
                                faculty = faculty_cell.get_text(strip=True) if faculty_cell else None
                                department = department_cell.get_text(strip=True) if department_cell else None
                                phones = phones_cell.get_text(strip=True) if phones_cell else None
                                
                                email = None
                                email_link = email_cell.find('a') if email_cell else None
                                if email_link:
                                    href = email_link.get('href', '')
                                    if href.startswith('mailto:'):
                                        email = href.replace('mailto:', '').strip()
                                    else:
                                        email = email_link.get_text(strip=True)
                                elif email_cell:
                                    email = email_cell.get_text(strip=True)
                                
                                if faculty and department:
                                    departments.append({
                                        "faculty": faculty,
                                        "department": department,
                                        "phones": phones if phones else None,
                                        "email": email if email else None
                                    })
                
                logger.info(f"Найдено деканатов: {len(deans)}, кафедр: {len(departments)}")
                return {
                    "success": True,
                    "deans": deans,
                    "departments": departments,
                    "error": None
                }
            elif response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if 'login' in location.lower():
                    return {"success": False, "deans": None, "departments": None, "error": "Требуется авторизация (редирект на страницу логина)"}
                else:
                    return {"success": False, "deans": None, "departments": None, "error": f"Неожиданный редирект: {location}"}
            else:
                return {"success": False, "deans": None, "departments": None, "error": f"Ошибка при получении контактов: HTTP {response.status_code}"}
                
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении контактов: {e}")
            return {"success": False, "deans": None, "departments": None, "error": f"Ошибка SSL соединения: {str(e)}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении контактов: {e}")
            return {"success": False, "deans": None, "departments": None, "error": f"Ошибка подключения к сайту: {str(e)}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении контактов: {e}")
            return {"success": False, "deans": None, "departments": None, "error": f"Неожиданная ошибка: {str(e)}"}
