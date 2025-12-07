"""Модуль для работы с расписанием"""
import requests
import re
import logging
import json
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .base import BaseScraper
from .utils import parse_date_to_dd_mm_yyyy, MONTHS_RU
from .personal_data import PersonalDataScraper

logger = logging.getLogger(__name__)

# Путь к файлу с данными о факультетах и группах
# Сохраняем в папке services
FACULTIES_GROUPS_FILE = os.path.join(os.path.dirname(__file__), 'faculties_groups.json')

# Путь к файлу с тестовым расписанием
TEST_SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), 'test_schedule.json')


def _convert_type_to_schedule_type(type_text: Optional[str]) -> str:
    """Преобразовать тип занятия в формат ScheduleType (lecture, practice, lab)"""
    if not type_text:
        return 'lecture'  # По умолчанию
    
    type_lower = type_text.lower()
    if 'лекц' in type_lower or type_lower == 'лк':
        return 'lecture'
    elif 'практик' in type_lower or type_lower == 'пр':
        return 'practice'
    elif 'лабораторн' in type_lower or type_lower == 'лб':
        return 'lab'
    else:
        return 'lecture'  # По умолчанию


def _detect_subgroup_from_text(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Определить подгруппу из текста
    
    Returns:
        tuple: (note, audience, undergruop)
        - note: "Общая пара" или "Подгруппа 1", "Подгруппа 2"
        - audience: 'full', 'subgroup1', 'subgroup2'
        - undergruop: "Подгруппа 1", "Подгруппа 2" или None
    """
    text_lower = text.lower()
    
    # Ищем упоминания подгрупп
    if re.search(r'подгруппа\s*1', text_lower):
        return ("Подгруппа 1", "subgroup1", "Подгруппа 1")
    elif re.search(r'подгруппа\s*2', text_lower):
        return ("Подгруппа 2", "subgroup2", "Подгруппа 2")
    elif re.search(r'1\s*подгрупп', text_lower):
        return ("Подгруппа 1", "subgroup1", "Подгруппа 1")
    elif re.search(r'2\s*подгрупп', text_lower):
        return ("Подгруппа 2", "subgroup2", "Подгруппа 2")
    else:
        return ("Общая пара", "full", None)


def _generate_lesson_id(subject: str, date: str, time_start: str, index: int = 0) -> str:
    """Сгенерировать уникальный ID для занятия"""
    # Создаем ID на основе предмета, даты и времени
    subject_slug = re.sub(r'[^a-zа-я0-9]', '-', subject.lower())[:20]
    date_slug = date.replace('.', '-')
    time_slug = time_start.replace(':', '-') if time_start else ''
    return f"{subject_slug}-{date_slug}-{time_slug}-{index}"


class ScheduleScraper(BaseScraper):
    """Класс для работы с расписанием"""
    
    def get_schedule(self, date_range: str, cookies_json: Optional[str] = None, lk_cookies_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить расписание со страницы tt.chuvsu.ru
        
        Алгоритм:
        1. Получить сайт tt.chuvsu.ru
        2. Найти в боковом блоке элементы факультетов
        3. Получить персональные данные студента (факультет и группа)
        4. Найти нужный id факультета по названию
        5. Скачать страницу с группами факультета
        6. Найти нужную кнопку группы по подстроке
        7. Перейти на страницу расписания группы
        8. Определить текущий период (осенний семестр, зимняя сессия, весенний семестр, летняя сессия)
        9. Получить расписание с параметрами pertype и htype
        
        Args:
            date_range: Промежуток дней в формате ДД.ММ-ДД.ММ (например: 10.11-03.12) или один день (например: 04.11)
            cookies_json: JSON строка с cookies от tt.chuvsu.ru (обязательно)
            lk_cookies_json: JSON строка с cookies от lk.chuvsu.ru (опционально, для получения personal_data)
        
        Returns:
            dict с ключами:
            - success: bool - успешно ли получены данные
            - schedule: list - список занятий (если успешно)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        try:
            logger.info(f"[SCHEDULE_SCRAPER] Начало получения расписания: date_range={date_range}")
            
            # ВРЕМЕННО: Используем тестовое расписание из JSON файла
            logger.info(f"[SCHEDULE_SCRAPER] Используем тестовое расписание из файла")
            test_schedule = self._load_or_generate_test_schedule()
            if test_schedule:
                filtered_schedule = self._repeat_week_for_date_range(test_schedule, date_range)
                logger.info(f"[SCHEDULE_SCRAPER] Возвращаем тестовое расписание: {len(filtered_schedule)} занятий")
                return {
                    "success": True,
                    "schedule": filtered_schedule,
                    "error": None
                }
            
            # Если тестовое расписание не загрузилось, продолжаем с реальным парсингом
            logger.warning(f"[SCHEDULE_SCRAPER] Тестовое расписание не найдено, используем реальный парсинг")
            
            if not cookies_json:
                logger.error("[SCHEDULE_SCRAPER] Cookies не предоставлены")
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Требуются cookies сессии от tt.chuvsu.ru"
                }
            
            # Устанавливаем cookies для tt.chuvsu.ru
            logger.info("[SCHEDULE_SCRAPER] Устанавливаем cookies для сессии")
            self.set_session_cookies(cookies_json)
            
            # Шаг 1: Получаем главную страницу tt.chuvsu.ru
            tt_base_url = "https://tt.chuvsu.ru"
            logger.info(f"[SCHEDULE_SCRAPER] Шаг 1: Получаем главную страницу {tt_base_url}")
            response = self.session.get(tt_base_url, timeout=30)
            logger.info(f"[SCHEDULE_SCRAPER] Получен ответ от главной страницы: status_code={response.status_code}")
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "schedule": None,
                    "error": f"Ошибка при получении главной страницы: HTTP {response.status_code}"
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Шаг 2: Находим боковой блок с факультетами
            logger.info("[SCHEDULE_SCRAPER] Шаг 2: Находим боковой блок с факультетами")
            # Ищем блок: <td valign="top" style="border-right: 1px solid #e0e0e0;" width="300">
            sidebar_td = soup.find('td', {
                'valign': 'top',
                'style': lambda x: x and 'border-right' in x and '1px solid' in x,
                'width': '300'
            })
            
            if not sidebar_td:
                logger.warning("[SCHEDULE_SCRAPER] sidebar_td не найден по основным атрибутам, пробуем найти по width='300'")
                # Пробуем найти по другим атрибутам
                sidebar_td = soup.find('td', {'width': '300'})
            
            if not sidebar_td:
                logger.error("[SCHEDULE_SCRAPER] Боковой блок с факультетами не найден. Ищем все td элементы:")
                all_tds = soup.find_all('td')
                logger.error(f"[SCHEDULE_SCRAPER] Найдено td элементов: {len(all_tds)}")
                for i, td in enumerate(all_tds[:5]):  # Показываем первые 5
                    logger.error(f"[SCHEDULE_SCRAPER] TD #{i+1} (width={td.get('width')}, style={td.get('style')}):\n{str(td)[:300]}")
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Боковой блок с факультетами не найден"
                }
            
            logger.info(f"[SCHEDULE_SCRAPER] Найден sidebar_td. HTML блока (первые 500 символов):\n{str(sidebar_td)[:500]}")
            
            # Находим все элементы факультетов: <div id="bt00" class="facbut" onclick="...">Название</div>
            logger.info("[SCHEDULE_SCRAPER] Ищем элементы факультетов (div с class='facbut')")
            faculty_divs = sidebar_td.find_all('div', {'class': 'facbut'})
            
            if not faculty_divs:
                logger.error("[SCHEDULE_SCRAPER] Элементы факультетов не найдены. Ищем все div в sidebar_td:")
                all_divs = sidebar_td.find_all('div')
                logger.error(f"[SCHEDULE_SCRAPER] Найдено div элементов: {len(all_divs)}")
                for i, div in enumerate(all_divs[:10]):  # Показываем первые 10
                    logger.error(f"[SCHEDULE_SCRAPER] Div #{i+1} (id={div.get('id')}, class={div.get('class')}):\n{str(div)[:200]}")
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Элементы факультетов не найдены"
                }
            
            logger.info(f"[SCHEDULE_SCRAPER] Найдено элементов факультетов: {len(faculty_divs)}")
            
            # Создаем словарь: название факультета -> id
            faculty_map = {}
            for div in faculty_divs:
                div_id = div.get('id', '')
                if div_id.startswith('bt'):
                    faculty_id = div_id[2:]  # Убираем префикс "bt"
                    faculty_name = div.get_text(strip=True)
                    if faculty_name:
                        faculty_map[faculty_name] = faculty_id
                        logger.debug(f"Найден факультет: {faculty_name} -> id={faculty_id}")
            
            if not faculty_map:
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Не удалось извлечь информацию о факультетах"
                }
            
            # Шаг 3: Получаем персональные данные студента для получения факультета и группы
            logger.info("[SCHEDULE_SCRAPER] Шаг 3: Получаем персональные данные студента")
            personal_data_scraper = PersonalDataScraper()
            personal_data_scraper.session = self.session
            personal_data_scraper.base_url = self.base_url
            personal_data_scraper.lk_base_url = self.lk_base_url
            
            # Для получения personal_data нужны cookies от lk.chuvsu.ru
            logger.info(f"[SCHEDULE_SCRAPER] Используем lk_cookies_json для получения personal_data")
            if not lk_cookies_json:
                logger.warning(f"[SCHEDULE_SCRAPER] lk_cookies_json не предоставлен, пробуем использовать tt_cookies")
                lk_cookies_json = cookies_json  # Fallback на tt cookies
            
            personal_data_result = personal_data_scraper.get_student_personal_data(cookies_json=lk_cookies_json)
            
            if not personal_data_result.get("success"):
                return {
                    "success": False,
                    "schedule": None,
                    "error": f"Не удалось получить персональные данные студента: {personal_data_result.get('error')}"
                }
            
            personal_data = personal_data_result.get("data", {})
            student_faculty = personal_data.get("faculty")
            student_group = personal_data.get("group")
            
            if not student_faculty:
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Факультет студента не найден в персональных данных"
                }
            
            if not student_group:
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Группа студента не найдена в персональных данных"
                }
            
            logger.info(f"Факультет студента: {student_faculty}, Группа: {student_group}")
            
            # Проверяем, есть ли данные в JSON файле
            logger.info(f"[SCHEDULE_SCRAPER] Проверяем наличие данных в JSON файле")
            group_id = None
            faculty_id = None
            faculty_name_from_json = None
            
            faculties_data = self._load_faculties_groups_data()
            if faculties_data:
                # Ищем факультет в JSON
                for fac_name, fac_data in faculties_data.items():
                    # Проверяем совпадение по названию факультета
                    if (student_faculty.lower() in fac_name.lower() or 
                        fac_name.lower() in student_faculty.lower() or
                        any(word in fac_name.lower() for word in student_faculty.lower().split() if len(word) > 3)):
                        faculty_id = fac_data.get("id")
                        faculty_name_from_json = fac_name
                        logger.info(f"[SCHEDULE_SCRAPER] Найден факультет в JSON: {fac_name} (id={faculty_id})")
                        
                        # Ищем группу в этом факультете
                        groups = fac_data.get("groups", [])
                        for group in groups:
                            group_name = group.get("name", "")
                            if student_group in group_name or group_name in student_group:
                                group_id = group.get("id")
                                logger.info(f"[SCHEDULE_SCRAPER] Найдена группа в JSON: {group_name} (id={group_id})")
                                break
                        
                        if group_id:
                            break
            
            # Если данные найдены в JSON, используем их
            if group_id and faculty_id:
                logger.info(f"[SCHEDULE_SCRAPER] Используем данные из JSON: faculty_id={faculty_id}, group_id={group_id}")
                # Пропускаем шаги 4-6 и переходим сразу к шагу 7
            else:
                logger.info(f"[SCHEDULE_SCRAPER] Данные не найдены в JSON, парсим с сайта")
                # Шаг 4: Находим нужный id факультета по названию
                logger.info(f"[SCHEDULE_SCRAPER] Шаг 4: Ищем факультет '{student_faculty}' в списке факультетов")
                # Ищем точное совпадение или частичное
                faculty_id = None
                for faculty_name, fac_id in faculty_map.items():
                    if student_faculty.lower() in faculty_name.lower() or faculty_name.lower() in student_faculty.lower():
                        faculty_id = fac_id
                        logger.info(f"Найден факультет по названию '{student_faculty}': {faculty_name} -> id={faculty_id}")
                        break
                
                if not faculty_id:
                    # Пробуем найти по первому слову или части названия
                    faculty_words = student_faculty.lower().split()
                    for faculty_name, fac_id in faculty_map.items():
                        faculty_name_lower = faculty_name.lower()
                        if any(word in faculty_name_lower for word in faculty_words if len(word) > 3):
                            faculty_id = fac_id
                            logger.info(f"Найден факультет по частичному совпадению: {faculty_name} -> id={faculty_id}")
                            break
                
                if not faculty_id:
                    return {
                        "success": False,
                        "schedule": None,
                        "error": f"Не удалось найти id факультета для '{student_faculty}'. Доступные факультеты: {list(faculty_map.keys())}"
                    }
                
                # Шаг 5: Скачиваем страницу с группами факультета
                logger.info(f"[SCHEDULE_SCRAPER] Шаг 5: Скачиваем страницу с группами факультета (faculty_id={faculty_id})")
                # https://tt.chuvsu.ru/index/factt/fac/00
                groups_url = f"{tt_base_url}/index/factt/fac/{faculty_id}"
                logger.info(f"Получаем страницу с группами факультета: {groups_url}")
                
                response = self.session.get(groups_url, timeout=30)
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "schedule": None,
                        "error": f"Ошибка при получении страницы с группами: HTTP {response.status_code}"
                    }
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Шаг 6: Находим форму с кнопками групп
                logger.info(f"[SCHEDULE_SCRAPER] Шаг 6: Ищем группу '{student_group}' в списке групп")
                logger.info("[SCHEDULE_SCRAPER] Ищем форму с id='tt' и method='post'")
                form = soup.find('form', {'id': 'tt', 'method': 'post'})
                
                if not form:
                    logger.error("[SCHEDULE_SCRAPER] Форма с группами не найдена. Ищем все формы:")
                    all_forms = soup.find_all('form')
                    logger.error(f"[SCHEDULE_SCRAPER] Найдено форм: {len(all_forms)}")
                    for i, f in enumerate(all_forms):
                        logger.error(f"[SCHEDULE_SCRAPER] Form #{i+1} (id={f.get('id')}, method={f.get('method')}):\n{str(f)[:300]}")
                    return {
                        "success": False,
                        "schedule": None,
                        "error": "Форма с группами не найдена"
                    }
                
                logger.info(f"[SCHEDULE_SCRAPER] Найдена форма. HTML блока (первые 500 символов):\n{str(form)[:500]}")
                
                # Находим все кнопки групп: <button name="gr9366" id="gr9366" ...>Название группы</button>
                logger.info("[SCHEDULE_SCRAPER] Ищем кнопки групп (button с type='button' и class='nicebut')")
                group_buttons = form.find_all('button', {'type': 'button', 'class': 'nicebut'})
                
                if not group_buttons:
                    logger.warning("[SCHEDULE_SCRAPER] Кнопки с class='nicebut' не найдены, пробуем найти все button с type='button'")
                    # Пробуем найти по другому классу или атрибутам
                    group_buttons = form.find_all('button', {'type': 'button'})
                
                if not group_buttons:
                    logger.error("[SCHEDULE_SCRAPER] Кнопки групп не найдены. Ищем все button элементы в форме:")
                    all_buttons = form.find_all('button')
                    logger.error(f"[SCHEDULE_SCRAPER] Найдено button элементов: {len(all_buttons)}")
                    for i, btn in enumerate(all_buttons[:10]):  # Показываем первые 10
                        logger.error(f"[SCHEDULE_SCRAPER] Button #{i+1} (id={btn.get('id')}, name={btn.get('name')}, class={btn.get('class')}, type={btn.get('type')}):\n{str(btn)[:200]}")
                    return {
                        "success": False,
                        "schedule": None,
                        "error": "Кнопки групп не найдены"
                    }
                
                logger.info(f"[SCHEDULE_SCRAPER] Найдено кнопок групп: {len(group_buttons)}")
                
                # Собираем данные о группах для сохранения в JSON
                groups_data = []
                for button in group_buttons:
                    button_id = button.get('id', '')
                    button_name = button.get('name', '')
                    button_text = button.get_text(strip=True)
                    
                    # Извлекаем id группы (цифры после "gr")
                    group_id_from_button = None
                    if button_id.startswith('gr'):
                        group_id_from_button = button_id[2:]  # Убираем префикс "gr"
                    elif button_name.startswith('gr'):
                        group_id_from_button = button_name[2:]
                    
                    if group_id_from_button and button_text:
                        groups_data.append({
                            "id": group_id_from_button,
                            "name": button_text
                        })
                
                # Сохраняем данные о факультете и его группах в JSON
                # Используем найденное название факультета из faculty_map
                faculty_name_for_save = None
                for fac_name, fac_id in faculty_map.items():
                    if fac_id == faculty_id:
                        faculty_name_for_save = fac_name
                        break
                
                if not faculty_name_for_save:
                    faculty_name_for_save = student_faculty  # Fallback на название из personal_data
                
                self._save_faculty_groups_data(faculty_id, faculty_name_for_save, groups_data)
                
                # Ищем нужную кнопку по названию группы (как подстрока)
                group_id = None
                for button in group_buttons:
                    button_id = button.get('id', '')
                    button_name = button.get('name', '')
                    button_text = button.get_text(strip=True)
                    
                    # Проверяем, что id и name начинаются с "gr"
                    if (button_id.startswith('gr') or button_name.startswith('gr')) and student_group in button_text:
                        # Извлекаем id группы (цифры после "gr")
                        if button_id.startswith('gr'):
                            group_id = button_id[2:]  # Убираем префикс "gr"
                        elif button_name.startswith('gr'):
                            group_id = button_name[2:]
                        
                        if group_id:
                            logger.info(f"Найдена группа '{student_group}' в кнопке '{button_text}' -> id={group_id}")
                            break
                
                if not group_id:
                    logger.error(f"[SCHEDULE_SCRAPER] Не удалось найти группу '{student_group}' среди доступных групп. Найдено групп: {len(group_buttons)}")
                    logger.error("[SCHEDULE_SCRAPER] Доступные группы:")
                    for i, button in enumerate(group_buttons[:20]):  # Показываем первые 20
                        button_id = button.get('id', '')
                        button_name = button.get('name', '')
                        button_text = button.get_text(strip=True)
                        logger.error(f"[SCHEDULE_SCRAPER] Группа #{i+1}: id={button_id}, name={button_name}, text='{button_text}'")
                    return {
                        "success": False,
                        "schedule": None,
                        "error": f"Не удалось найти группу '{student_group}' среди доступных групп. Найдено групп: {len(group_buttons)}"
                    }
            
            # Шаг 7: Переходим на страницу расписания группы
            logger.info(f"[SCHEDULE_SCRAPER] Шаг 7: Переходим на страницу расписания группы (group_id={group_id})")
            # https://tt.chuvsu.ru/index/grouptt/gr/9366
            schedule_url = f"{tt_base_url}/index/grouptt/gr/{group_id}"
            logger.info(f"[SCHEDULE_SCRAPER] Обращаемся к URL: {schedule_url}")
            logger.info(f"[SCHEDULE_SCRAPER] Метод: GET")
            
            response = self.session.get(schedule_url, timeout=30)
            
            logger.info(f"[SCHEDULE_SCRAPER] Получен ответ: status_code={response.status_code}, content_length={len(response.text)}")
            
            if response.status_code != 200:
                logger.error(f"[SCHEDULE_SCRAPER] Ошибка при получении расписания: HTTP {response.status_code}")
                logger.error(f"[SCHEDULE_SCRAPER] URL: {schedule_url}")
                logger.error(f"[SCHEDULE_SCRAPER] Ответ (первые 500 символов): {response.text[:500]}")
                return {
                    "success": False,
                    "schedule": None,
                    "error": f"Ошибка при получении расписания: HTTP {response.status_code}"
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info(f"[SCHEDULE_SCRAPER] HTML страницы распарсен, размер: {len(response.text)} символов")
            
            # Шаг 8: Определяем текущий период (осенний семестр, зимняя сессия, весенний семестр, летняя сессия)
            logger.info("[SCHEDULE_SCRAPER] Шаг 8: Определяем текущий период и неделю")
            # Ищем блок: <div style="margin-top: 30px;" width="100%"><center>...<p>идет 11<sup>*</sup> неделя осеннего семестра</p>...</center></div>
            period_info = None
            period_number = None
            week_number = None
            current_date = None
            current_weekday = None  # 0 = понедельник, 6 = воскресенье
            
            # Ищем div с информацией о периоде
            # Ищем div с информацией о периоде: должен содержать <center> и <span> с датой или <p> с информацией о неделе
            logger.info("[SCHEDULE_SCRAPER] Ищем div с информацией о периоде (style содержит 'margin-top' и '30px', и содержит center)")
            # Сначала ищем все div с margin-top: 30px
            all_divs_with_margin_30 = soup.find_all('div', {'style': lambda x: x and 'margin-top' in x and '30px' in x if x else False})
            logger.info(f"[SCHEDULE_SCRAPER] Найдено div с margin-top: 30px: {len(all_divs_with_margin_30)}")
            
            period_div = None
            # Ищем div, который содержит <center> (это должен быть правильный блок)
            for div in all_divs_with_margin_30:
                center = div.find('center')
                if center:
                    period_div = div
                    logger.info(f"[SCHEDULE_SCRAPER] Найден period_div с center. HTML блока:\n{str(period_div)[:500]}")
                    break
            
            # Если не нашли с center, пробуем найти div, который содержит span с датой или p с информацией о неделе
            if not period_div:
                logger.info("[SCHEDULE_SCRAPER] Не найден div с center, ищем div с span или p с информацией о периоде")
                for div in all_divs_with_margin_30:
                    # Проверяем, содержит ли div span с датой или p с информацией о неделе
                    has_date_span = div.find('span', {'style': lambda x: x and 'color: blue' in x if x else False})
                    has_period_p = div.find('p')
                    if has_date_span or (has_period_p and re.search(r'идет\s+\d+', has_period_p.get_text(), re.IGNORECASE)):
                        period_div = div
                        logger.info(f"[SCHEDULE_SCRAPER] Найден period_div по содержимому. HTML блока:\n{str(period_div)[:500]}")
                        break
            if period_div:
                logger.info(f"[SCHEDULE_SCRAPER] Найден period_div. Полный HTML блока:\n{str(period_div)}")
                logger.info(f"[SCHEDULE_SCRAPER] Текст period_div: {period_div.get_text()}")
                logger.info(f"[SCHEDULE_SCRAPER] Все дочерние элементы period_div:")
                for child in period_div.children:
                    if hasattr(child, 'name'):
                        logger.info(f"[SCHEDULE_SCRAPER]   - {child.name}: {str(child)[:200]}")
                    elif str(child).strip():
                        logger.info(f"[SCHEDULE_SCRAPER]   - текст: {str(child)[:200]}")
                # Извлекаем дату из <span style="color: blue; font-size: 20px;">13 Ноября 2025г.<br></span>
                logger.info("[SCHEDULE_SCRAPER] Ищем span с датой (style содержит 'color: blue' и 'font-size: 20px')")
                date_span = period_div.find('span', {'style': lambda x: x and 'color: blue' in x and 'font-size: 20px' in x})
                if date_span:
                    logger.info(f"[SCHEDULE_SCRAPER] Найден date_span. HTML блока:\n{str(date_span)}")
                    date_text = date_span.get_text(strip=True).replace('г.', '').strip()
                    logger.info(f"[SCHEDULE_SCRAPER] Найден текст даты: {date_text}")
                    
                    # Парсим дату: "13 Ноября 2025"
                    try:
                        parts = date_text.split()
                        if len(parts) == 3:
                            day = int(parts[0])
                            month_name = parts[1].lower()
                            year = int(parts[2])
                            
                            month = MONTHS_RU.get(month_name)
                            if month:
                                current_date = datetime(year, month, day)
                                logger.info(f"[SCHEDULE_SCRAPER] Распарсена дата: {current_date.strftime('%d.%m.%Y')}")
                            else:
                                logger.error(f"[SCHEDULE_SCRAPER] Неизвестный месяц: {month_name}")
                        else:
                            logger.error(f"[SCHEDULE_SCRAPER] Неверный формат даты: {date_text} (ожидается 3 части, получено {len(parts)})")
                    except Exception as e:
                        logger.error(f"[SCHEDULE_SCRAPER] Ошибка при парсинге даты '{date_text}': {e}")
                else:
                    logger.warning(f"[SCHEDULE_SCRAPER] date_span не найден. Ищем все span элементы в period_div:")
                    all_spans = period_div.find_all('span')
                    logger.warning(f"[SCHEDULE_SCRAPER] Найдено span элементов: {len(all_spans)}")
                    for i, span in enumerate(all_spans):
                        logger.warning(f"[SCHEDULE_SCRAPER] Span #{i+1} (style={span.get('style')}):\n{str(span)}")
                    # Пробуем найти span с другим стилем
                    logger.warning("[SCHEDULE_SCRAPER] Пробуем найти span с любым стилем, содержащим 'blue' или '20px':")
                    for span in period_div.find_all('span'):
                        style = span.get('style', '')
                        if 'blue' in style.lower() or '20px' in style.lower():
                            logger.warning(f"[SCHEDULE_SCRAPER] Найден span с подходящим стилем: style={style}, HTML={str(span)}")
                
                # Извлекаем день недели (текст после даты, например "Четверг")
                center_text = period_div.get_text()
                logger.info(f"[SCHEDULE_SCRAPER] Полный текст period_div: {center_text[:200]}")
                weekday_names = {
                    'понедельник': 0, 'вторник': 1, 'среда': 2, 'четверг': 3,
                    'пятница': 4, 'суббота': 5, 'воскресенье': 6
                }
                for name, num in weekday_names.items():
                    if name in center_text.lower():
                        current_weekday = num
                        logger.info(f"[SCHEDULE_SCRAPER] Определен день недели: {name} ({current_weekday})")
                        break
                
                # Ищем параграф с информацией о неделе и периоде
                logger.info("[SCHEDULE_SCRAPER] Ищем параграф <p> с информацией о неделе и периоде")
                period_p = period_div.find('p')
                if period_p:
                    logger.info(f"[SCHEDULE_SCRAPER] Найден period_p. HTML блока:\n{str(period_p)}")
                    period_text = period_p.get_text(strip=True)
                    logger.info(f"[SCHEDULE_SCRAPER] Найден текст периода: {period_text}")
                    
                    # Парсим число недели (может быть с <sup>*</sup>)
                    week_match = re.search(r'идет\s+(\d+)', period_text, re.IGNORECASE)
                    if week_match:
                        week_number = int(week_match.group(1))
                        logger.info(f"[SCHEDULE_SCRAPER] Извлечен номер недели: {week_number}")
                    else:
                        logger.warning(f"[SCHEDULE_SCRAPER] Не удалось найти номер недели в тексте: {period_text}")
                    
                    # Определяем период по ключевым словам
                    period_text_lower = period_text.lower()
                    if 'осен' in period_text_lower:
                        period_number = 1  # Осенний семестр
                        period_info = "осенний семестр"
                    elif 'зимн' in period_text_lower:
                        period_number = 2  # Зимняя сессия
                        period_info = "зимняя сессия"
                    elif 'весен' in period_text_lower:
                        period_number = 3  # Весенний семестр
                        period_info = "весенний семестр"
                    elif 'летн' in period_text_lower:
                        period_number = 4  # Летняя сессия
                        period_info = "летняя сессия"
                    
                    if period_number:
                        logger.info(f"[SCHEDULE_SCRAPER] Определен период: {period_info} (номер: {period_number}), неделя: {week_number}")
                    else:
                        logger.warning(f"[SCHEDULE_SCRAPER] Не удалось определить период из текста: {period_text}")
                else:
                    logger.warning(f"[SCHEDULE_SCRAPER] period_p не найден. Ищем все параграфы в period_div:")
                    all_ps = period_div.find_all('p')
                    logger.warning(f"[SCHEDULE_SCRAPER] Найдено параграфов: {len(all_ps)}")
                    for i, p in enumerate(all_ps):
                        logger.warning(f"[SCHEDULE_SCRAPER] P #{i+1}:\n{str(p)}")
                    # Пробуем найти информацию о периоде в любом тексте period_div
                    logger.warning("[SCHEDULE_SCRAPER] Пробуем найти информацию о периоде в тексте period_div:")
                    full_text = period_div.get_text()
                    logger.warning(f"[SCHEDULE_SCRAPER] Полный текст period_div:\n{full_text}")
                    # Ищем паттерн "идет X неделя"
                    week_match = re.search(r'идет\s+(\d+)', full_text, re.IGNORECASE)
                    if week_match:
                        logger.warning(f"[SCHEDULE_SCRAPER] Найден номер недели в тексте: {week_match.group(1)}")
                    # Ищем период
                    if 'осен' in full_text.lower():
                        logger.warning("[SCHEDULE_SCRAPER] Найден период: осенний семестр")
                    elif 'зимн' in full_text.lower():
                        logger.warning("[SCHEDULE_SCRAPER] Найден период: зимняя сессия")
                    elif 'весен' in full_text.lower():
                        logger.warning("[SCHEDULE_SCRAPER] Найден период: весенний семестр")
                    elif 'летн' in full_text.lower():
                        logger.warning("[SCHEDULE_SCRAPER] Найден период: летняя сессия")
            else:
                logger.error("[SCHEDULE_SCRAPER] period_div не найден. Ищем все div с margin-top:")
                all_divs_with_margin = soup.find_all('div', {'style': lambda x: x and 'margin-top' in x if x else False})
                logger.error(f"[SCHEDULE_SCRAPER] Найдено div с margin-top: {len(all_divs_with_margin)}")
                for i, div in enumerate(all_divs_with_margin[:5]):  # Показываем первые 5
                    logger.error(f"[SCHEDULE_SCRAPER] Div #{i+1}:\n{str(div)[:300]}")
            
            if not period_number or week_number is None:
                logger.error(f"[SCHEDULE_SCRAPER] ОШИБКА: period_number={period_number}, week_number={week_number}")
                logger.error(f"[SCHEDULE_SCRAPER] HTML страницы (первые 2000 символов):\n{response.text[:2000]}")
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Не удалось определить текущий период или номер недели"
                }
            
            if not current_date or current_weekday is None:
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Не удалось определить текущую дату или день недели"
                }
            
            # Шаг 9: Получаем расписание с параметрами pertype и htype
            logger.info(f"[SCHEDULE_SCRAPER] Шаг 9: Получаем расписание с параметрами pertype={period_number}, htype={period_number}")
            # Нужно отправить POST запрос с параметрами "pertype"="N" и "htype"="N", где N - номер периода
            logger.info(f"[SCHEDULE_SCRAPER] Получаем расписание с параметрами pertype={period_number}, htype={period_number}")
            
            # Формируем URL для POST запроса (может быть тот же или другой)
            schedule_post_url = schedule_url  # Или может быть другой URL
            logger.info(f"[SCHEDULE_SCRAPER] Обращаемся к URL: {schedule_post_url}")
            logger.info(f"[SCHEDULE_SCRAPER] Метод: POST")
            logger.info(f"[SCHEDULE_SCRAPER] POST данные: pertype={period_number}, htype={period_number}")
            
            response = self.session.post(
                schedule_post_url,
                data={
                    "pertype": str(period_number),
                    "htype": str(period_number)
                },
                timeout=30
            )
            
            logger.info(f"[SCHEDULE_SCRAPER] Получен ответ: status_code={response.status_code}, content_length={len(response.text)}")
            
            if response.status_code != 200:
                logger.error(f"[SCHEDULE_SCRAPER] Ошибка при получении расписания с параметрами периода: HTTP {response.status_code}")
                logger.error(f"[SCHEDULE_SCRAPER] URL: {schedule_post_url}")
                logger.error(f"[SCHEDULE_SCRAPER] POST данные: pertype={period_number}, htype={period_number}")
                logger.error(f"[SCHEDULE_SCRAPER] Ответ (первые 500 символов): {response.text[:500]}")
                return {
                    "success": False,
                    "schedule": None,
                    "error": f"Ошибка при получении расписания с параметрами периода: HTTP {response.status_code}"
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info(f"[SCHEDULE_SCRAPER] Успешно получена страница с расписанием группы с параметрами периода. HTML размер: {len(response.text)} символов")
            
            # Шаг 10: Парсим таблицу расписания
            logger.info("[SCHEDULE_SCRAPER] Шаг 10: Парсим таблицу расписания")
            logger.info(f"[SCHEDULE_SCRAPER] Ищем таблицу расписания (table с id='groupstt')")
            logger.info(f"[SCHEDULE_SCRAPER] URL страницы: {schedule_post_url}")
            schedule_table = soup.find('table', {'id': 'groupstt'})
            if not schedule_table:
                logger.error(f"[SCHEDULE_SCRAPER] Таблица расписания не найдена на URL: {schedule_post_url}")
                logger.error("[SCHEDULE_SCRAPER] Ищем все таблицы:")
                all_tables = soup.find_all('table')
                logger.error(f"[SCHEDULE_SCRAPER] Найдено таблиц: {len(all_tables)}")
                for i, table in enumerate(all_tables):
                    logger.error(f"[SCHEDULE_SCRAPER] Table #{i+1} (id={table.get('id')}, class={table.get('class')}):\n{str(table)[:500]}")
                logger.error(f"[SCHEDULE_SCRAPER] HTML страницы (первые 3000 символов):\n{response.text[:3000]}")
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Таблица расписания (id='groupstt') не найдена"
                }
            
            logger.info(f"[SCHEDULE_SCRAPER] ✓ Таблица расписания найдена! (id='groupstt')")
            logger.info(f"[SCHEDULE_SCRAPER] HTML блока (первые 1000 символов):\n{str(schedule_table)[:1000]}")
            
            # Вычисляем дату понедельника (вычитаем current_weekday дней)
            monday_date = current_date - timedelta(days=current_weekday)
            logger.info(f"Дата понедельника: {monday_date.strftime('%d.%m.%Y')}")
            
            schedule = []
            change_list = []  # Список для предметов с красной рамкой
            
            # Находим все строки таблицы
            rows = schedule_table.find_all('tr')
            logger.info(f"[SCHEDULE_SCRAPER] Найдено строк в таблице: {len(rows)}")
            current_day = None  # Текущий день недели (0 = понедельник)
            current_pair_time = None  # Время текущей пары
            current_pair_number = None  # Номер текущей пары
            
            i = 0
            days_found = 0
            pairs_found = 0
            subjects_found = 0
            subjects_filtered_by_week = 0
            logger.info(f"[SCHEDULE_SCRAPER] Начинаем парсинг {len(rows)} строк таблицы")
            while i < len(rows):
                row = rows[i]
                row_class = row.get('class', [])
                
                # Проверяем, является ли строка заголовком дня недели
                if 'trfd' in row_class:
                    # Это день недели, определяем какой
                    day_text = row.get_text(strip=True).lower()
                    day_mapping = {
                        'понедельник': 0, 'вторник': 1, 'среда': 2, 'четверг': 3,
                        'пятница': 4, 'суббота': 5, 'воскресенье': 6
                    }
                    for day_name, day_num in day_mapping.items():
                        if day_name in day_text:
                            current_day = day_num
                            days_found += 1
                            logger.info(f"[SCHEDULE_SCRAPER] Найден день недели: {day_name} ({current_day})")
                            break
                    i += 1
                    continue
                
                # Проверяем, является ли строка парой (even или odd, но не trfd)
                if ('even' in row_class or 'odd' in row_class) and 'trfd' not in row_class:
                    cells = row.find_all('td')
                    logger.debug(f"[SCHEDULE_SCRAPER] Строка с классом {row_class}, найдено {len(cells)} ячеек")
                    if len(cells) >= 2:
                        # Первая ячейка - номер пары и время
                        time_cell = cells[0]
                        time_cell_classes = time_cell.get('class', [])
                        logger.debug(f"[SCHEDULE_SCRAPER] Первая ячейка: классы={time_cell_classes}, текст='{time_cell.get_text(strip=True)[:100]}'")
                        if 'trf' in time_cell_classes and 'trdata' in time_cell_classes:
                            time_text = time_cell.get_text(strip=True)
                            # Парсим "1 пара (8:20 - 9:40)"
                            pair_match = re.search(r'(\d+)\s+пара\s+\((\d+:\d+)\s+-\s+(\d+:\d+)\)', time_text)
                            if pair_match:
                                current_pair_number = int(pair_match.group(1))
                                time_start = pair_match.group(2)
                                time_end = pair_match.group(3)
                                current_pair_time = (time_start, time_end)
                                pairs_found += 1
                                logger.info(f"[SCHEDULE_SCRAPER] Найдена пара {current_pair_number}: {time_start} - {time_end}, день={current_day}")
                            else:
                                logger.warning(f"[SCHEDULE_SCRAPER] Не удалось распарсить время пары из текста: '{time_text}'")
                        else:
                            logger.debug(f"[SCHEDULE_SCRAPER] Первая ячейка не содержит нужных классов (trf и trdata)")
                        
                        # Вторая ячейка - блоки с предметами
                        subjects_cell = cells[1]
                        subject_rows = subjects_cell.find_all('tr')
                        if pairs_found > 0 and current_pair_number is not None:
                            logger.info(f"[SCHEDULE_SCRAPER] В паре {current_pair_number} найдено {len(subject_rows)} строк с предметами")
                        
                        for subject_row in subject_rows:
                            subject_td = subject_row.find('td', {'class': 'want'})
                            if not subject_td:
                                logger.debug(f"[SCHEDULE_SCRAPER] Пропущена строка без td.want")
                                continue
                            
                            subjects_found += 1
                        
                            # Проверяем, есть ли красная рамка (может быть отдельный блок или встроенная)
                            red_border_divs = subject_td.find_all('div', {
                                'style': lambda x: x and 'border: 2px solid red' in x
                            })
                            
                            # Проверяем тип изменения
                            # Тип 1: весь блок в красной рамке (перенос с более поздней даты)
                            first_child = next(subject_td.children, None)
                            is_type_1 = (first_child and first_child.name == 'div' and 
                                       'border: 2px solid red' in first_child.get('style', ''))
                            
                            if is_type_1:
                                # Это тип 1 - отдельный блок переноса
                                change_list.append({
                                    'html': str(subject_row),
                                    'day': current_day,
                                    'pair_number': current_pair_number,
                                    'time_start': current_pair_time[0] if current_pair_time else None,
                                    'time_end': current_pair_time[1] if current_pair_time else None,
                                    'type': 1  # Тип изменения
                                })
                                logger.info(f"[SCHEDULE_SCRAPER] Добавлен предмет типа 1 (перенос) в change_list, день={current_day}, пара={current_pair_number}")
                                continue
                        
                            # Типы 2 и 3: встроенные изменения в нормальном блоке
                            if red_border_divs:
                                # Определяем тип: если есть "перенос на" - тип 2, иначе тип 3
                                change_type = 2 if any('перенос на' in div.get_text() for div in red_border_divs) else 3
                                change_list.append({
                                    'html': str(subject_row),
                                    'day': current_day,
                                    'pair_number': current_pair_number,
                                    'time_start': current_pair_time[0] if current_pair_time else None,
                                    'time_end': current_pair_time[1] if current_pair_time else None,
                                    'type': change_type
                                })
                                logger.debug(f"Добавлен предмет с встроенными изменениями типа {change_type} в change_list")
                            
                            # Получаем текст без изменений (удаляем div с красной рамкой для парсинга основного предмета)
                            subject_td_copy = BeautifulSoup(str(subject_td), 'html.parser')
                            for div in subject_td_copy.find_all('div', {'style': lambda x: x and 'border: 2px solid red' in x}):
                                div.decompose()
                            
                            subject_text = subject_td_copy.get_text(separator=' ', strip=True)
                            
                            # Извлекаем кабинет (до синего span)
                            room = None
                            blue_span = subject_td_copy.find('span', {'style': lambda x: x and 'color: blue' in x})
                            if blue_span:
                                # Кабинет - это весь текст до синего span
                                room_parts = []
                                for element in subject_td_copy.descendants:
                                    if element == blue_span:
                                        break
                                    if isinstance(element, str) and element.strip():
                                        room_parts.append(element.strip())
                                
                                if room_parts:
                                    room = ' '.join(room_parts).strip()
                                    room = ' '.join(room.split())
                            
                            # Название предмета (из синего span)
                            subject_name = blue_span.get_text(strip=True) if blue_span else None
                            
                            # Тип пары: (пр), (лб), (лк)
                            type_match = re.search(r'\((пр|лб|лк)\)', subject_text)
                            type_text = None
                            if type_match:
                                type_abbr = type_match.group(1)
                                type_map = {'лк': 'Лекция', 'пр': 'Практика', 'лб': 'Лабораторная'}
                                type_text = type_map.get(type_abbr, type_abbr)
                        
                            # Недели: (10 - 13 нед.)
                            weeks_match = re.search(r'\((\d+)\s*-\s*(\d+)\s*нед\.\)', subject_text)
                            week_start = None
                            week_end = None
                            if weeks_match:
                                week_start = int(weeks_match.group(1))
                                week_end = int(weeks_match.group(2))
                            
                            # Проверяем, попадает ли текущая неделя в промежуток
                            if week_start is not None and week_end is not None:
                                if not (week_start <= week_number <= week_end):
                                    subjects_filtered_by_week += 1
                                    logger.info(f"[SCHEDULE_SCRAPER] Предмет '{subject_name}' не попадает в неделю {week_number} (недели {week_start}-{week_end}), день={current_day}, пара={current_pair_number}")
                                    continue
                            elif week_start is None or week_end is None:
                                logger.warning(f"[SCHEDULE_SCRAPER] Не удалось определить недели для предмета '{subject_name}', subject_text: {subject_text[:200]}")
                            
                            # Преподаватель - текст после типа пары и недель
                            teacher = None
                            additional_info = None
                            
                            # Извлекаем преподавателя и доп. информацию
                            br_tag = subject_td_copy.find('br')
                            if br_tag:
                                teacher_text = ''.join(br_tag.next_siblings).strip()
                                if teacher_text:
                                    lines = [line.strip() for line in teacher_text.split('\n') if line.strip()]
                                    if lines:
                                        teacher = lines[0]
                                        if len(lines) > 1:
                                            additional_info = '\n'.join(lines[1:])
                            else:
                                if weeks_match:
                                    weeks_pos = subject_text.find(weeks_match.group(0))
                                    if weeks_pos != -1:
                                        after_weeks = subject_text[weeks_pos + len(weeks_match.group(0)):].strip()
                                        if after_weeks:
                                            lines = [line.strip() for line in after_weeks.split('\n') if line.strip()]
                                            if lines:
                                                teacher = lines[0]
                                                if len(lines) > 1:
                                                    additional_info = '\n'.join(lines[1:])
                            
                            # Вычисляем дату для этого дня недели
                            lesson_date = monday_date + timedelta(days=current_day)
                            date_str = lesson_date.strftime("%d.%m.%Y")
                            time_start = current_pair_time[0] if current_pair_time else None
                            time_end = current_pair_time[1] if current_pair_time else None
                            
                            # Определяем подгруппу из текста
                            note, audience, undergruop = _detect_subgroup_from_text(subject_text)
                            
                            # Преобразуем тип занятия
                            schedule_type = _convert_type_to_schedule_type(type_text)
                            
                            # Генерируем ID
                            lesson_id = _generate_lesson_id(subject_name or '', date_str, time_start or '', subjects_found)
                            
                            # Добавляем в расписание в новом формате
                            lesson = {
                                "id": lesson_id,
                                "start": time_start or "",
                                "end": time_end or "",
                                "title": subject_name or "",
                                "type": schedule_type,
                                "room": room or "",
                                "note": note,
                                "audience": audience,
                                "date": date_str,
                                "teacher": teacher,
                                "additional_info": additional_info if additional_info else None,
                                "undergruop": undergruop
                            }
                            schedule.append(lesson)
                            logger.info(f"[SCHEDULE_SCRAPER] ✓ Добавлен предмет: '{subject_name}' на {lesson['date']} {lesson['start']}, день={current_day}, пара={current_pair_number}")
                    else:
                        # Строка не является парой (even/odd без trfd), но не прошла проверку на пару
                        logger.debug(f"[SCHEDULE_SCRAPER] Строка с классом {row_class} не распознана как пара (ячеек: {len(cells)})")
                else:
                    # Строка не является ни днем недели, ни парой
                    logger.debug(f"[SCHEDULE_SCRAPER] Строка с классом {row_class} не распознана (не день недели и не пара)")
                
                i += 1
            
            logger.info(f"[SCHEDULE_SCRAPER] Парсинг таблицы завершен")
            logger.info(f"[SCHEDULE_SCRAPER] Статистика парсинга:")
            logger.info(f"[SCHEDULE_SCRAPER]   - Дней недели найдено: {days_found}")
            logger.info(f"[SCHEDULE_SCRAPER]   - Пар найдено: {pairs_found}")
            logger.info(f"[SCHEDULE_SCRAPER]   - Предметов найдено: {subjects_found}")
            logger.info(f"[SCHEDULE_SCRAPER]   - Предметов отфильтровано по неделе: {subjects_filtered_by_week}")
            logger.info(f"[SCHEDULE_SCRAPER]   - Занятий добавлено в расписание: {len(schedule)}")
            logger.info(f"[SCHEDULE_SCRAPER]   - Предметов с изменениями: {len(change_list)}")
            if len(schedule) == 0:
                logger.warning(f"[SCHEDULE_SCRAPER] ⚠ ВНИМАНИЕ: Расписание пустое! Найдено 0 занятий")
                logger.warning(f"[SCHEDULE_SCRAPER] URL: {schedule_post_url}")
                logger.warning(f"[SCHEDULE_SCRAPER] Параметры: pertype={period_number}, htype={period_number}, week_number={week_number}")
                logger.warning(f"[SCHEDULE_SCRAPER] Строк в таблице: {len(rows)}")
                logger.warning(f"[SCHEDULE_SCRAPER] Дней недели: {days_found}, Пар: {pairs_found}, Предметов: {subjects_found}, Отфильтровано: {subjects_filtered_by_week}")
            
            # Обрабатываем изменения из change_list
            logger.info(f"[SCHEDULE_SCRAPER] Обрабатываем {len(change_list)} изменений в расписании")
            self._process_changes(schedule, change_list, monday_date, week_number)
            logger.info(f"[SCHEDULE_SCRAPER] После обработки изменений: {len(schedule)} занятий")
            
            # Фильтруем по date_range (используем год из current_date)
            logger.info(f"[SCHEDULE_SCRAPER] Фильтруем расписание по date_range={date_range}, year={current_date.year}")
            filtered_schedule = self._filter_by_date_range(schedule, date_range, current_date.year)
            
            logger.info(f"[SCHEDULE_SCRAPER] После обработки изменений и фильтрации: {len(filtered_schedule)} занятий")
            
            return {
                "success": True,
                "schedule": filtered_schedule,
                "error": None
            }
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении расписания: {e}")
            return {
                "success": False,
                "schedule": None,
                "error": f"Ошибка SSL соединения: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении расписания: {e}")
            return {
                "success": False,
                "schedule": None,
                "error": f"Ошибка подключения к сайту: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении расписания: {e}")
            return {
                "success": False,
                "schedule": None,
                "error": f"Неожиданная ошибка: {str(e)}"
            }
    
    def _process_changes(self, schedule: List[Dict], change_list: List[Dict], monday_date: datetime, week_number: int):
        """Обработать изменения из change_list и применить их к расписанию"""
        for change in change_list:
            try:
                change_html = change['html']
                change_type = change.get('type', 1)
                change_soup = BeautifulSoup(change_html, 'html.parser')
                change_td = change_soup.find('td', {'class': 'want'})
                
                if not change_td:
                    continue
                
                if change_type == 1:
                    # Тип 1: Перенос с более поздней даты на более раннюю
                    # Формат: "08.12.2025 перенос c 10.11.2025 (2 пара):"
                    red_span = change_td.find('span', {'style': lambda x: x and 'color: red' in x})
                    if red_span:
                        red_text = red_span.get_text(strip=True)
                        # Парсим: "08.12.2025 перенос c 10.11.2025 (2 пара):"
                        transfer_match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s+перенос\s+c\s+(\d{2}\.\d{2}\.\d{4})\s+\((\d+)\s+пара\)', red_text)
                        if transfer_match:
                            new_date_str = transfer_match.group(1)  # 08.12.2025
                            old_date_str = transfer_match.group(2)   # 10.11.2025
                            old_pair = int(transfer_match.group(3))  # 2
                            
                            # Парсим новую дату
                            new_date = datetime.strptime(new_date_str, "%d.%m.%Y")
                            
                            # Удаляем старую пару из расписания
                            schedule[:] = [lesson for lesson in schedule 
                                         if not (lesson.get('date') == old_date_str and 
                                                self._get_pair_number(lesson.get('start')) == old_pair)]
                            
                            # Парсим новый предмет из блока
                            lesson_data = self._parse_lesson_from_change(change_td, new_date_str, change.get('time_start'), change.get('time_end'))
                            if lesson_data:
                                schedule.append(lesson_data)
                                logger.debug(f"Обработан перенос типа 1: {old_date_str} ({old_pair} пара) -> {new_date_str}")
                
                elif change_type == 2:
                    # Тип 2: Перенос с одной даты на другую (встроен в блок предмета)
                    # Сначала парсим основной предмет
                    main_lesson = self._parse_main_lesson_from_change(change_td, change, monday_date, week_number)
                    if not main_lesson:
                        continue
                    
                    # Находим все блоки переноса
                    red_divs = change_td.find_all('div', {'style': lambda x: x and 'border: 2px solid red' in x})
                    for red_div in red_divs:
                        red_text = red_div.get_text()
                        if 'перенос на' in red_text:
                            # Парсим: "13.11.2025  перенос на: 02.12.2025 (1 пара)"
                            transfer_match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s+перенос\s+на:', red_text)
                            if transfer_match:
                                old_date_str = transfer_match.group(1)  # 13.11.2025
                                
                                # Ищем новую дату и пару
                                new_date_span = red_div.find('span', {'class': 'blue'})
                                pair_match = re.search(r'\((\d+)\s+пара\)', red_text)
                                
                                if new_date_span and pair_match:
                                    new_date_str = new_date_span.get_text(strip=True)  # 02.12.2025
                                    new_pair = int(pair_match.group(1))  # 1
                                    
                                    # Получаем время для новой пары (нужно найти по номеру пары)
                                    new_time = self._get_time_for_pair(new_pair, change.get('time_start'))
                                    
                                    # Удаляем старую пару
                                    schedule[:] = [lesson for lesson in schedule 
                                                 if not (lesson.get('date') == old_date_str and 
                                                        lesson.get('title') == main_lesson.get('title') and
                                                        self._get_pair_number(lesson.get('start')) == change.get('pair_number'))]
                                    
                                    # Добавляем новую пару
                                    new_lesson = main_lesson.copy()
                                    new_lesson['date'] = new_date_str
                                    new_lesson['start'] = new_time[0] if new_time else ""
                                    new_lesson['end'] = new_time[1] if new_time else ""
                                    # Обновляем ID для новой даты
                                    new_lesson['id'] = _generate_lesson_id(new_lesson.get('title', ''), new_date_str, new_lesson['start'], 0)
                                    schedule.append(new_lesson)
                                    logger.debug(f"Обработан перенос типа 2: {old_date_str} -> {new_date_str} ({new_pair} пара)")
                
                elif change_type == 3:
                    # Тип 3: Замена преподавателя
                    # Сначала парсим основной предмет
                    main_lesson = self._parse_main_lesson_from_change(change_td, change, monday_date, week_number)
                    if not main_lesson:
                        continue
                    
                    # Находим все блоки замены
                    red_divs = change_td.find_all('div', {'style': lambda x: x and 'border: 2px solid red' in x})
                    for red_div in red_divs:
                        red_text = red_div.get_text()
                        if 'замена на' in red_text:
                            # Парсим: "21.11.2025  замена на: Преподаватель: Долгушева В. И."
                            replace_match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s+замена\s+на:', red_text)
                            if replace_match:
                                change_date_str = replace_match.group(1)  # 21.11.2025
                                
                                # Ищем нового преподавателя
                                teacher_span = red_div.find('span', {'class': 'blue'})
                                if teacher_span:
                                    new_teacher = teacher_span.get_text(strip=True)
                                    
                                    # Обновляем преподавателя в расписании
                                    for lesson in schedule:
                                        if (lesson.get('date') == change_date_str and 
                                            lesson.get('title') == main_lesson.get('title') and
                                            self._get_pair_number(lesson.get('start')) == change.get('pair_number')):
                                            lesson['teacher'] = new_teacher
                                            logger.debug(f"Обработана замена преподавателя типа 3: {change_date_str} -> {new_teacher}")
                                            break
            except Exception as e:
                logger.error(f"Ошибка при обработке изменения: {e}")
                continue
    
    def _parse_lesson_from_change(self, change_td, date_str: str, time_start: Optional[str], time_end: Optional[str]) -> Optional[Dict]:
        """Парсить предмет из блока изменения"""
        try:
            # Убираем красную рамку для парсинга
            change_td_copy = BeautifulSoup(str(change_td), 'html.parser')
            for div in change_td_copy.find_all('div', {'style': lambda x: x and 'border: 2px solid red' in x}):
                div.decompose()
            for span in change_td_copy.find_all('span', {'style': lambda x: x and 'color: red' in x}):
                span.decompose()
            
            text = change_td_copy.get_text(separator=' ', strip=True)
            
            # Парсим кабинет, предмет, тип, преподавателя
            blue_span = change_td_copy.find('span', {'style': lambda x: x and 'color: blue' in x})
            if not blue_span:
                return None
            
            subject_name = blue_span.get_text(strip=True)
            
            # Кабинет
            room_parts = []
            for element in change_td_copy.descendants:
                if element == blue_span:
                    break
                if isinstance(element, str) and element.strip():
                    room_parts.append(element.strip())
            room = ' '.join(room_parts).strip() if room_parts else None
            
            # Тип
            type_match = re.search(r'\((пр|лб|лк)\)', text)
            type_text = None
            if type_match:
                type_abbr = type_match.group(1)
                type_map = {'лк': 'Лекция', 'пр': 'Практика', 'лб': 'Лабораторная'}
                type_text = type_map.get(type_abbr, type_abbr)
            
            # Преподаватель (после <br>)
            teacher = None
            br_tag = change_td_copy.find('br')
            if br_tag:
                teacher_text = ''.join(br_tag.next_siblings).strip()
                if teacher_text:
                    lines = [line.strip() for line in teacher_text.split('\n') if line.strip()]
                    if lines:
                        teacher = lines[0]
            
            # Определяем подгруппу из текста
            note, audience, undergruop = _detect_subgroup_from_text(text)
            
            # Преобразуем тип занятия
            schedule_type = _convert_type_to_schedule_type(type_text)
            
            # Генерируем ID
            lesson_id = _generate_lesson_id(subject_name or '', date_str, time_start or '', 0)
            
            return {
                "id": lesson_id,
                "start": time_start or "",
                "end": time_end or "",
                "title": subject_name or "",
                "type": schedule_type,
                "room": room or "",
                "note": note,
                "audience": audience,
                "date": date_str,
                "teacher": teacher,
                "additional_info": None,
                "undergruop": undergruop
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге предмета из изменения: {e}")
            return None
    
    def _parse_main_lesson_from_change(self, change_td, change: Dict, monday_date: datetime, week_number: int) -> Optional[Dict]:
        """Парсить основной предмет из блока с изменениями"""
        try:
            # Убираем красные рамки
            change_td_copy = BeautifulSoup(str(change_td), 'html.parser')
            for div in change_td_copy.find_all('div', {'style': lambda x: x and 'border: 2px solid red' in x}):
                div.decompose()
            
            text = change_td_copy.get_text(separator=' ', strip=True)
            
            blue_span = change_td_copy.find('span', {'style': lambda x: x and 'color: blue' in x})
            if not blue_span:
                return None
            
            subject_name = blue_span.get_text(strip=True)
            
            # Кабинет
            room_parts = []
            for element in change_td_copy.descendants:
                if element == blue_span:
                    break
                if isinstance(element, str) and element.strip():
                    room_parts.append(element.strip())
            room = ' '.join(room_parts).strip() if room_parts else None
            
            # Тип
            type_match = re.search(r'\((пр|лб|лк)\)', text)
            type_text = None
            if type_match:
                type_abbr = type_match.group(1)
                type_map = {'лк': 'Лекция', 'пр': 'Практика', 'лб': 'Лабораторная'}
                type_text = type_map.get(type_abbr, type_abbr)
            
            # Недели
            weeks_match = re.search(r'\((\d+)\s*-\s*(\d+)\s*нед\.\)', text)
            week_start = None
            week_end = None
            if weeks_match:
                week_start = int(weeks_match.group(1))
                week_end = int(weeks_match.group(2))
            
            if week_start and week_end and not (week_start <= week_number <= week_end):
                return None
            
            # Преподаватель
            teacher = None
            br_tag = change_td_copy.find('br')
            if br_tag:
                teacher_text = ''.join(br_tag.next_siblings).strip()
                if teacher_text:
                    lines = [line.strip() for line in teacher_text.split('\n') if line.strip()]
                    if lines:
                        teacher = lines[0]
            
            # Дата
            lesson_date = monday_date + timedelta(days=change.get('day', 0))
            date_str = lesson_date.strftime("%d.%m.%Y")
            time_start = change.get('time_start')
            time_end = change.get('time_end')
            
            # Определяем подгруппу из текста
            note, audience, undergruop = _detect_subgroup_from_text(text)
            
            # Преобразуем тип занятия
            schedule_type = _convert_type_to_schedule_type(type_text)
            
            # Генерируем ID
            lesson_id = _generate_lesson_id(subject_name or '', date_str, time_start or '', 0)
            
            return {
                "id": lesson_id,
                "start": time_start or "",
                "end": time_end or "",
                "title": subject_name or "",
                "type": schedule_type,
                "room": room or "",
                "note": note,
                "audience": audience,
                "date": date_str,
                "teacher": teacher,
                "additional_info": None,
                "undergruop": undergruop
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге основного предмета: {e}")
            return None
    
    def _get_pair_number(self, time_start: Optional[str]) -> Optional[int]:
        """Получить номер пары по времени начала"""
        if not time_start:
            return None
        # Точное соответствие времени и номера пары
        time_pairs = {
            "8:20": 1, "8:30": 1,
            "9:50": 2, "10:00": 2,
            "11:20": 3, "11:30": 3,
            "13:00": 4, "13:10": 4,
            "14:30": 5, "14:40": 5,
            "16:00": 6, "16:10": 6,
            "17:30": 7, "17:40": 7
        }
        # Проверяем точное совпадение
        if time_start in time_pairs:
            return time_pairs[time_start]
        # Проверяем по началу (часы:минуты)
        time_parts = time_start.split(':')
        if len(time_parts) == 2:
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            # Приблизительное определение по часам
            if hours == 8 or (hours == 9 and minutes < 50):
                return 1
            elif hours == 9 or (hours == 10 and minutes < 20):
                return 2
            elif hours == 11 or (hours == 12 and minutes < 0):
                return 3
            elif hours == 13 or (hours == 14 and minutes < 30):
                return 4
            elif hours == 14 or (hours == 15 and minutes < 50):
                return 5
            elif hours == 16 or (hours == 17 and minutes < 30):
                return 6
            elif hours == 17 or hours == 18:
                return 7
        return None
    
    def _get_time_for_pair(self, pair_number: int, default_time_start: Optional[str]) -> Optional[tuple]:
        """Получить время для номера пары"""
        time_pairs = {
            1: ("8:20", "9:40"),
            2: ("9:50", "11:10"),
            3: ("11:20", "12:40"),
            4: ("13:00", "14:20"),
            5: ("14:30", "15:50"),
            6: ("16:00", "17:20"),
            7: ("17:30", "18:50")
        }
        return time_pairs.get(pair_number)
    
    def _filter_by_date_range(self, schedule: List[Dict], date_range: str, year: int) -> List[Dict]:
        """Фильтровать расписание по диапазону дат или одному дню
        
        Поддерживает:
        - Диапазон дат: "10.11-03.12" или "20.12-05.01"
        - Один день: "04.11"
        
        Учитывает переход на новый год (например, 20.12-05.01)
        """
        try:
            # Парсим диапазон: "10.11-03.12", "20.12-05.01" или один день "04.11"
            parts = date_range.split('-')
            
            if len(parts) == 1:
                # Один день: "04.11"
                single_date_str = parts[0].strip()
                start_date = datetime.strptime(f"{single_date_str}.{year}", "%d.%m.%Y")
                end_date = start_date  # Один и тот же день
            elif len(parts) == 2:
                # Диапазон дат: "10.11-03.12"
                start_str = parts[0].strip()  # "10.11" или "20.12"
                end_str = parts[1].strip()    # "03.12" или "05.01"
                
                start_month = int(start_str.split('.')[1])
                end_month = int(end_str.split('.')[1])
                
                # Если диапазон пересекает границу года (например, ноябрь-декабрь или декабрь-январь)
                # start_month > end_month означает переход на новый год
                if start_month > end_month:
                    # Начало в текущем году, конец в следующем
                    # Например: 20.12-05.01 -> 20.12.2025 - 05.01.2026
                    start_date = datetime.strptime(f"{start_str}.{year}", "%d.%m.%Y")
                    end_date = datetime.strptime(f"{end_str}.{year + 1}", "%d.%m.%Y")
                else:
                    # Оба в одном году
                    # Например: 10.11-03.12 -> 10.11.2025 - 03.12.2025
                    start_date = datetime.strptime(f"{start_str}.{year}", "%d.%m.%Y")
                    end_date = datetime.strptime(f"{end_str}.{year}", "%d.%m.%Y")
            else:
                logger.warning(f"Неверный формат date_range: {date_range}")
                return schedule
            
            filtered = []
            for lesson in schedule:
                lesson_date_str = lesson.get('date')
                if lesson_date_str:
                    try:
                        lesson_date = datetime.strptime(lesson_date_str, "%d.%m.%Y")
                        if start_date <= lesson_date <= end_date:
                            filtered.append(lesson)
                    except ValueError:
                        logger.warning(f"Неверный формат даты в занятии: {lesson_date_str}")
                        continue
            
            return filtered
        except Exception as e:
            logger.error(f"Ошибка при фильтрации по date_range: {e}")
            return schedule
    
    def _load_faculties_groups_data(self) -> Dict[str, Any]:
        """Загрузить данные о факультетах и группах из JSON файла
        
        Returns:
            dict с данными о факультетах и группах или пустой dict, если файл не существует
        """
        try:
            if not os.path.exists(FACULTIES_GROUPS_FILE):
                logger.info(f"[SCHEDULE_SCRAPER] Файл {FACULTIES_GROUPS_FILE} не существует")
                return {}
            
            with open(FACULTIES_GROUPS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"[SCHEDULE_SCRAPER] Загружены данные из {FACULTIES_GROUPS_FILE}: {len(data)} факультетов")
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"[SCHEDULE_SCRAPER] Ошибка при чтении файла {FACULTIES_GROUPS_FILE}: {e}")
            return {}
        except Exception as e:
            logger.error(f"[SCHEDULE_SCRAPER] Неожиданная ошибка при загрузке данных: {e}")
            return {}
    
    def _save_faculty_groups_data(self, faculty_id: str, faculty_name: str, groups: List[Dict]):
        """Сохранить данные о факультете и его группах в JSON файл
        
        Args:
            faculty_id: ID факультета
            faculty_name: Название факультета
            groups: Список групп [{"id": "9366", "name": "ИЯ-02-25"}, ...]
        """
        try:
            # Загружаем существующие данные, если файл существует
            faculties_data = {}
            if os.path.exists(FACULTIES_GROUPS_FILE):
                try:
                    with open(FACULTIES_GROUPS_FILE, 'r', encoding='utf-8') as f:
                        faculties_data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"[SCHEDULE_SCRAPER] Ошибка при чтении существующего файла {FACULTIES_GROUPS_FILE}: {e}")
                    faculties_data = {}
            
            # Обновляем данные для текущего факультета
            # Используем название факультета как ключ
            faculties_data[faculty_name] = {
                "id": faculty_id,
                "groups": groups
            }
            
            # Сохраняем обновленные данные
            os.makedirs(os.path.dirname(FACULTIES_GROUPS_FILE), exist_ok=True)
            with open(FACULTIES_GROUPS_FILE, 'w', encoding='utf-8') as f:
                json.dump(faculties_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[SCHEDULE_SCRAPER] Сохранены данные о факультете '{faculty_name}' (id={faculty_id}) с {len(groups)} группами в {FACULTIES_GROUPS_FILE}")
        except Exception as e:
            logger.error(f"[SCHEDULE_SCRAPER] Ошибка при сохранении данных о факультетах и группах: {e}")
    
    def _generate_test_schedule(self) -> List[Dict]:
        """Сгенерировать тестовое расписание на одну неделю (понедельник-воскресенье)"""
        # Берем текущую дату и находим понедельник этой недели
        today = datetime.now()
        days_since_monday = today.weekday()  # 0 = понедельник, 6 = воскресенье
        monday = today - timedelta(days=days_since_monday)
        
        # Тестовое расписание на неделю
        test_schedule = []
        lesson_index = 0
        
        def create_lesson(date_str: str, start: str, end: str, title: str, type_str: str, 
                         teacher: str, room: str, note: str = "Общая пара", 
                         audience: str = "full", undergruop: Optional[str] = None,
                         additional_info: Optional[str] = None) -> Dict:
            nonlocal lesson_index
            lesson_id = _generate_lesson_id(title, date_str, start, lesson_index)
            lesson_index += 1
            return {
                "id": lesson_id,
                "start": start,
                "end": end,
                "title": title,
                "type": _convert_type_to_schedule_type(type_str),
                "room": room,
                "note": note,
                "audience": audience,
                "date": date_str,
                "teacher": teacher,
                "additional_info": additional_info,
                "undergruop": undergruop
            }
        
        # Понедельник
        monday_str = (monday + timedelta(days=0)).strftime("%d.%m.%Y")
        test_schedule.extend([
            create_lesson(monday_str, "8:20", "9:40", "Математический анализ", "Лекция", 
                         "Иванов И.И.", "Ауд. 101"),
            create_lesson(monday_str, "9:50", "11:10", "Программирование", "Практика", 
                         "Петров П.П.", "Ауд. 205"),
            create_lesson(monday_str, "11:20", "12:40", "Физика", "Лекция", 
                         "Сидоров С.С.", "Ауд. 301")
        ])
        
        # Вторник
        tuesday_str = (monday + timedelta(days=1)).strftime("%d.%m.%Y")
        test_schedule.extend([
            create_lesson(tuesday_str, "8:20", "9:40", "Алгоритмы и структуры данных", "Лекция", 
                         "Козлов К.К.", "Ауд. 102"),
            create_lesson(tuesday_str, "13:00", "14:20", "Базы данных", "Практика", 
                         "Новиков Н.Н.", "Ауд. 206")
        ])
        
        # Среда
        wednesday_str = (monday + timedelta(days=2)).strftime("%d.%m.%Y")
        test_schedule.extend([
            create_lesson(wednesday_str, "9:50", "11:10", "Веб-разработка", "Практика", 
                         "Морозов М.М.", "Ауд. 207"),
            create_lesson(wednesday_str, "11:20", "12:40", "Операционные системы", "Лекция", 
                         "Волков В.В.", "Ауд. 302"),
            create_lesson(wednesday_str, "14:30", "15:50", "Иностранный язык", "Практика", 
                         "Смирнова С.С.", "Ауд. 401")
        ])
        
        # Четверг
        thursday_str = (monday + timedelta(days=3)).strftime("%d.%m.%Y")
        test_schedule.extend([
            create_lesson(thursday_str, "8:20", "9:40", "Компьютерные сети", "Лекция", 
                         "Лебедев Л.Л.", "Ауд. 103"),
            create_lesson(thursday_str, "13:00", "14:20", "Машинное обучение", "Лекция", 
                         "Федоров Ф.Ф.", "Ауд. 303")
        ])
        
        # Пятница
        friday_str = (monday + timedelta(days=4)).strftime("%d.%m.%Y")
        test_schedule.extend([
            create_lesson(friday_str, "9:50", "11:10", "Проектирование ПО", "Практика", 
                         "Орлов О.О.", "Ауд. 208"),
            create_lesson(friday_str, "11:20", "12:40", "Кибербезопасность", "Лекция", 
                         "Романов Р.Р.", "Ауд. 304")
        ])
        
        # Суббота (обычно пар меньше)
        saturday_str = (monday + timedelta(days=5)).strftime("%d.%m.%Y")
        test_schedule.extend([
            create_lesson(saturday_str, "8:20", "9:40", "Физкультура", "Практика", 
                         "Спортов С.С.", "Спортзал")
        ])
        
        # Воскресенье - выходной, пар нет
        
        return test_schedule
    
    def _load_or_generate_test_schedule(self) -> Optional[List[Dict]]:
        """Загрузить тестовое расписание из файла или сгенерировать новое"""
        try:
            # Пытаемся загрузить из файла
            if os.path.exists(TEST_SCHEDULE_FILE):
                with open(TEST_SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"[SCHEDULE_SCRAPER] Загружено тестовое расписание из {TEST_SCHEDULE_FILE}: {len(data)} занятий")
                    return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"[SCHEDULE_SCRAPER] Ошибка при чтении тестового расписания: {e}")
        
        # Если файл не существует или ошибка чтения, генерируем новое
        logger.info(f"[SCHEDULE_SCRAPER] Генерируем новое тестовое расписание")
        test_schedule = self._generate_test_schedule()
        
        # Сохраняем в файл
        try:
            os.makedirs(os.path.dirname(TEST_SCHEDULE_FILE), exist_ok=True)
            with open(TEST_SCHEDULE_FILE, 'w', encoding='utf-8') as f:
                json.dump(test_schedule, f, ensure_ascii=False, indent=2)
            logger.info(f"[SCHEDULE_SCRAPER] Сохранено тестовое расписание в {TEST_SCHEDULE_FILE}: {len(test_schedule)} занятий")
        except Exception as e:
            logger.error(f"[SCHEDULE_SCRAPER] Ошибка при сохранении тестового расписания: {e}")
        
        return test_schedule
    
    def _repeat_week_for_date_range(self, week_schedule: List[Dict], date_range: str) -> List[Dict]:
        """Повторить недельное расписание для указанного диапазона дат или одного дня
        
        Поддерживает:
        - Диапазон дат: "10.11-03.12" или "20.12-05.01"
        - Один день: "04.11"
        """
        try:
            # Парсим диапазон дат или один день
            parts = date_range.split('-')
            
            # Определяем год (берем текущий)
            current_year = datetime.now().year
            
            if len(parts) == 1:
                # Один день: "04.11"
                single_date_str = parts[0].strip()
                start_date = datetime.strptime(f"{single_date_str}.{current_year}", "%d.%m.%Y")
                end_date = start_date  # Один и тот же день
            elif len(parts) == 2:
                # Диапазон дат: "10.11-03.12"
                start_str = parts[0].strip()  # "10.11"
                end_str = parts[1].strip()    # "03.12"
                
                # Парсим даты
                start_month = int(start_str.split('.')[1])
                end_month = int(end_str.split('.')[1])
                
                if start_month > end_month:
                    # Переход через год
                    start_date = datetime.strptime(f"{start_str}.{current_year}", "%d.%m.%Y")
                    end_date = datetime.strptime(f"{end_str}.{current_year + 1}", "%d.%m.%Y")
                else:
                    start_date = datetime.strptime(f"{start_str}.{current_year}", "%d.%m.%Y")
                    end_date = datetime.strptime(f"{end_str}.{current_year}", "%d.%m.%Y")
            else:
                logger.warning(f"[SCHEDULE_SCRAPER] Неверный формат date_range: {date_range}")
                return week_schedule
            
            # Находим понедельник первой недели
            days_since_monday = start_date.weekday()
            first_monday = start_date - timedelta(days=days_since_monday)
            
            # Получаем дату первого занятия из недельного расписания
            if not week_schedule:
                return []
            
            first_lesson_date_str = week_schedule[0].get("date")
            if not first_lesson_date_str:
                return week_schedule
            
            first_lesson_date = datetime.strptime(first_lesson_date_str, "%d.%m.%Y")
            week_offset = (first_monday - first_lesson_date).days
            
            # Генерируем расписание для всех недель в диапазоне
            result_schedule = []
            current_week_start = first_monday
            
            while current_week_start <= end_date:
                # Добавляем занятия для текущей недели
                for lesson in week_schedule:
                    lesson_date = datetime.strptime(lesson["date"], "%d.%m.%Y")
                    new_lesson_date = lesson_date + timedelta(days=week_offset)
                    
                    # Проверяем, попадает ли занятие в диапазон
                    if start_date <= new_lesson_date <= end_date:
                        new_lesson = lesson.copy()
                        new_date_str = new_lesson_date.strftime("%d.%m.%Y")
                        new_lesson["date"] = new_date_str
                        # Обновляем ID для новой даты
                        new_lesson["id"] = _generate_lesson_id(
                            new_lesson.get("title", ""), 
                            new_date_str, 
                            new_lesson.get("start", ""), 
                            len(result_schedule)
                        )
                        result_schedule.append(new_lesson)
                
                # Переходим к следующей неделе
                current_week_start += timedelta(days=7)
                week_offset += 7
            
            logger.info(f"[SCHEDULE_SCRAPER] Сгенерировано расписание для диапазона {date_range}: {len(result_schedule)} занятий")
            return result_schedule
            
        except Exception as e:
            logger.error(f"[SCHEDULE_SCRAPER] Ошибка при повторении недели для date_range: {e}")
            return week_schedule