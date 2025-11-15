"""Модуль для работы с новостями"""
import requests
import logging
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)

# Путь к файлу с тестовыми новостями
TEST_NEWS_FILE = os.path.join(os.path.dirname(__file__), 'test_news.json')


class NewsScraper(BaseScraper):
    """Класс для работы с новостями"""
    
    def get_news(self, limit: int = 10, cookies_json: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить новости университета
        
        Args:
            limit: Максимальное количество новостей для возврата (по умолчанию 10)
            cookies_json: JSON строка с cookies от lk.chuvsu.ru (опционально)
        
        Returns:
            dict с ключами:
            - success: bool - успешно ли получены данные
            - news: list - список новостей (если успешно)
            - error: str - сообщение об ошибке (если неуспешно)
        """
        try:
            logger.info(f"[NEWS_SCRAPER] Начало получения новостей: limit={limit}")
            
            # ВРЕМЕННО: Используем тестовые новости из JSON файла
            logger.info(f"[NEWS_SCRAPER] Используем тестовые новости из файла")
            test_news = self._load_or_generate_test_news()
            if test_news:
                # Ограничиваем количество новостей
                limited_news = test_news[:limit] if limit > 0 else test_news
                logger.info(f"[NEWS_SCRAPER] Возвращаем тестовые новости: {len(limited_news)} из {len(test_news)}")
                return {
                    "success": True,
                    "news": limited_news,
                    "error": None
                }
            
            # Если тестовые новости не загрузились, продолжаем с реальным парсингом
            logger.warning(f"[NEWS_SCRAPER] Тестовые новости не найдены, используем реальный парсинг")
            
            if not cookies_json:
                logger.warning("[NEWS_SCRAPER] Cookies не предоставлены, пробуем получить новости без авторизации")
            
            # Устанавливаем cookies, если они предоставлены
            if cookies_json:
                logger.info("[NEWS_SCRAPER] Устанавливаем cookies для сессии")
                self.set_session_cookies(cookies_json)
            
            # TODO: Реализовать реальный парсинг новостей с сайта университета
            # Пример URL: https://www.chuvsu.ru/news или https://lk.chuvsu.ru/news
            
            # Временная заглушка - возвращаем пустой список
            logger.warning("[NEWS_SCRAPER] Реальный парсинг новостей еще не реализован")
            return {
                "success": False,
                "news": None,
                "error": "Парсинг новостей с сайта университета еще не реализован. Используйте тестовые данные."
            }
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении новостей: {e}")
            return {
                "success": False,
                "news": None,
                "error": f"Ошибка SSL соединения: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении новостей: {e}")
            return {
                "success": False,
                "news": None,
                "error": f"Ошибка подключения к сайту: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении новостей: {e}")
            return {
                "success": False,
                "news": None,
                "error": f"Неожиданная ошибка: {str(e)}"
            }
    
    def _generate_test_news(self) -> List[Dict]:
        """Сгенерировать тестовые новости"""
        today = datetime.now()
        
        test_news = []
        
        # Генерируем 20 тестовых новостей
        news_titles = [
            "Открытие нового учебного корпуса",
            "Студенческая конференция по информационным технологиям",
            "Награждение лучших студентов семестра",
            "Мастер-класс от ведущих специалистов индустрии",
            "Спортивные соревнования между факультетами",
            "Новая программа обмена студентами",
            "День открытых дверей для абитуриентов",
            "Запуск нового онлайн-курса",
            "Встреча с выпускниками университета",
            "Научная конференция по современным исследованиям",
            "Обновление библиотечного фонда",
            "Конкурс студенческих проектов",
            "Волонтерская акция в рамках социального проекта",
            "Семинар по карьерному развитию",
            "Выставка студенческих работ",
            "Турнир по программированию",
            "Лекция приглашенного профессора",
            "Обновление расписания занятий",
            "Информация о стипендиальных программах",
            "Культурное мероприятие в университете"
        ]
        
        news_contents = [
            "Университет рад сообщить об открытии нового современного учебного корпуса, оснащенного передовым оборудованием.",
            "Приглашаем всех желающих принять участие в студенческой конференции, посвященной актуальным вопросам IT-индустрии.",
            "Состоялась торжественная церемония награждения студентов, показавших отличные результаты в учебе.",
            "Ведущие специалисты проведут мастер-класс для студентов старших курсов.",
            "Завершились межфакультетские спортивные соревнования, определившие лучшие команды.",
            "Объявлен набор на программу международного обмена студентами на следующий семестр.",
            "Приглашаем абитуриентов и их родителей на день открытых дверей.",
            "Доступен новый онлайн-курс по современным технологиям разработки.",
            "Состоится встреча с успешными выпускниками, которые поделятся опытом.",
            "Научная конференция соберет исследователей из разных областей знаний.",
            "Библиотека пополнилась новыми изданиями по актуальным направлениям.",
            "Объявлен конкурс на лучший студенческий проект года.",
            "Студенты примут участие в волонтерской акции помощи нуждающимся.",
            "Семинар поможет студентам спланировать свою карьеру.",
            "В главном корпусе открылась выставка творческих работ студентов.",
            "Состоится турнир по спортивному программированию среди студентов.",
            "Приглашенный профессор прочитает лекцию по актуальной теме.",
            "Опубликовано обновленное расписание занятий на следующий семестр.",
            "Информация о новых стипендиальных программах и условиях получения.",
            "В университете пройдет культурное мероприятие с участием студентов."
        ]
        
        for i, (title, content) in enumerate(zip(news_titles, news_contents)):
            # Создаем даты от сегодня назад
            news_date = today - timedelta(days=i)
            
            test_news.append({
                "id": f"news_{i+1}",
                "title": title,
                "content": content,
                "date": news_date.strftime("%d.%m.%Y"),
                "author": f"Администрация университета",
                "category": "Общие новости" if i % 3 == 0 else ("Учеба" if i % 3 == 1 else "События"),
                "image_url": None,
                "link": f"https://www.chuvsu.ru/news/{i+1}"
            })
        
        return test_news
    
    def _load_or_generate_test_news(self) -> Optional[List[Dict]]:
        """Загрузить тестовые новости из файла или сгенерировать новые"""
        try:
            # Пытаемся загрузить из файла
            if os.path.exists(TEST_NEWS_FILE):
                with open(TEST_NEWS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    news = data.get('news', [])
                    logger.info(f"[NEWS_SCRAPER] Загружены тестовые новости из {TEST_NEWS_FILE}: {len(news)} новостей")
                    return news
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"[NEWS_SCRAPER] Ошибка при чтении тестовых новостей: {e}")
        
        # Если файл не существует или ошибка чтения, генерируем новые
        logger.info(f"[NEWS_SCRAPER] Генерируем новые тестовые новости")
        test_news = self._generate_test_news()
        
        # Сохраняем в файл
        try:
            os.makedirs(os.path.dirname(TEST_NEWS_FILE), exist_ok=True)
            with open(TEST_NEWS_FILE, 'w', encoding='utf-8') as f:
                json.dump({"news": test_news}, f, ensure_ascii=False, indent=2)
            logger.info(f"[NEWS_SCRAPER] Сохранены тестовые новости в {TEST_NEWS_FILE}: {len(test_news)} новостей")
        except Exception as e:
            logger.error(f"[NEWS_SCRAPER] Ошибка при сохранении тестовых новостей: {e}")
        
        return test_news


