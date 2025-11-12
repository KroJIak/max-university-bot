"""Модуль для работы с расписанием"""
import requests
import re
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper
from .utils import parse_date_to_dd_mm_yyyy

logger = logging.getLogger(__name__)


class ScheduleScraper(BaseScraper):
    """Класс для работы с расписанием"""
    
    def get_schedule(self, week: int = 1, cookies_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить расписание со страницы https://lk.chuvsu.ru/student/tt.php
        
        Args:
            week: Номер недели (1 = текущая неделя, 2 = следующая неделя)
                  Внутренне преобразуется в tabact (1 -> 3, 2 -> 4)
            cookies_json: JSON строка с cookies от lk.chuvsu.ru (обязательно)
        
        Returns:
            dict с ключами:
            - success: bool - успешно ли получены данные
            - schedule: list - список занятий (если успешно)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        try:
            if cookies_json:
                self.set_session_cookies(cookies_json)
            
            # Преобразуем week (1, 2) в tabact (3, 4)
            if week == 1:
                tabact = 3
            elif week == 2:
                tabact = 4
            else:
                logger.warning(f"Неверный номер недели: {week}, используем текущую неделю (tabact=3)")
                tabact = 3
            
            schedule_url = f"{self.lk_base_url}/student/tt.php"
            
            response = self.session.post(
                schedule_url,
                data={"tabact": str(tabact)},
                allow_redirects=False,
                timeout=30
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                tables = soup.find_all('table')
                
                if not tables:
                    return {"success": False, "schedule": None, "error": "Таблица расписания не найдена"}
                
                # Ищем таблицу с наибольшим количеством строк
                best_table = None
                best_row_count = 0
                
                for table in tables:
                    tbody = table.find('tbody')
                    rows = tbody.find_all('tr') if tbody else table.find_all('tr')
                    if len(rows) > best_row_count:
                        best_row_count = len(rows)
                        best_table = table
                
                if not best_table:
                    best_table = tables[0]
                
                schedule = []
                current_date = None
                rows = best_table.find('tbody').find_all('tr') if best_table.find('tbody') else best_table.find_all('tr')
                
                for idx, row in enumerate(rows):
                    cells = row.find_all('td')
                    if len(cells) == 0:
                        continue
                    
                    # Проверяем, является ли строка заголовком даты
                    style = row.get('style', '')
                    is_date_row = False
                    
                    if style and ('background' in style.lower() and 'lightgray' in style.lower()):
                        if len(cells) == 1:
                            cell = cells[0]
                            colspan = cell.get('colspan', '')
                            if colspan == '2' or colspan == 2:
                                date_text = cell.get_text(strip=True)
                                if date_text:
                                    current_date = parse_date_to_dd_mm_yyyy(date_text)
                                    is_date_row = True
                    
                    if not is_date_row and len(cells) == 1:
                        cell = cells[0]
                        colspan = cell.get('colspan', '')
                        if colspan == '2' or colspan == 2:
                            date_text = cell.get_text(strip=True)
                            if date_text and any(month in date_text.lower() for month in ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']):
                                current_date = parse_date_to_dd_mm_yyyy(date_text)
                                is_date_row = True
                    
                    if is_date_row:
                        continue
                    
                    if len(cells) >= 2:
                        time_cell = cells[0]
                        lesson_cell = cells[1]
                        time_nobr = time_cell.find('nobr')
                        
                        if not time_nobr:
                            continue
                        
                        if not current_date:
                            current_date = "Неизвестная дата"
                        
                        time_text = time_nobr.get_text(strip=True)
                        if not time_text or '-' not in time_text:
                            continue
                        
                        time_parts = time_text.split('-')
                        if len(time_parts) != 2:
                            continue
                        
                        time_start = time_parts[0].strip()
                        time_end = time_parts[1].strip()
                        lesson_text = lesson_cell.get_text(separator=' ', strip=True)
                        subject_span = lesson_cell.find('span', {'class': 'blue'})
                        
                        if not subject_span:
                            continue
                        
                        subject = subject_span.get_text(strip=True)
                        lesson_after_subject = lesson_text[len(subject):].strip()
                        type_match = re.search(r'\(([лп][кбр])\)', lesson_after_subject)
                        type_text = None
                        type_abbr = None
                        
                        if type_match:
                            type_abbr = type_match.group(1)
                            type_map = {'лк': 'Лекция', 'пр': 'Практика', 'лб': 'Лабораторная'}
                            type_text = type_map.get(type_abbr, type_abbr)
                        
                        room = None
                        room_span = lesson_cell.find('span', {'class': 'red'})
                        if room_span:
                            room = room_span.get_text(strip=True)
                        
                        teacher = None
                        if type_match and room_span:
                            type_pos = lesson_after_subject.find(f'({type_abbr})')
                            if type_pos != -1:
                                after_type = lesson_after_subject[type_pos + len(f'({type_abbr})'):].strip()
                                room_pos_in_text = after_type.find(room)
                                if room_pos_in_text != -1:
                                    teacher_text = after_type[:room_pos_in_text].strip()
                                    if teacher_text:
                                        teacher = teacher_text
                        
                        additional_info = None
                        if room_span:
                            ital_span = lesson_cell.find('span', {'class': 'ital'})
                            if ital_span:
                                additional_info = ital_span.get_text(strip=True)
                            else:
                                room_pos = lesson_text.find(room)
                                if room_pos != -1:
                                    after_room = lesson_text[room_pos + len(room):].strip()
                                    if after_room:
                                        additional_info = after_room.strip('()').strip()
                                        if not additional_info:
                                            additional_info = None
                        
                        lesson = {
                            "date": current_date,
                            "time_start": time_start,
                            "time_end": time_end,
                            "subject": subject,
                            "type": type_text,
                            "teacher": teacher,
                            "room": room,
                            "additional_info": additional_info if additional_info else None
                        }
                        schedule.append(lesson)
                
                logger.info(f"Найдено занятий в расписании: {len(schedule)}")
                return {"success": True, "schedule": schedule, "error": None}
            elif response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if 'login' in location.lower():
                    return {"success": False, "schedule": None, "error": "Требуется авторизация (редирект на страницу логина)"}
                else:
                    return {"success": False, "schedule": None, "error": f"Неожиданный редирект: {location}"}
            else:
                return {"success": False, "schedule": None, "error": f"Ошибка при получении расписания: HTTP {response.status_code}"}
                
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении расписания: {e}")
            return {"success": False, "schedule": None, "error": f"Ошибка SSL соединения: {str(e)}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении расписания: {e}")
            return {"success": False, "schedule": None, "error": f"Ошибка подключения к сайту: {str(e)}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении расписания: {e}")
            return {"success": False, "schedule": None, "error": f"Неожиданная ошибка: {str(e)}"}
