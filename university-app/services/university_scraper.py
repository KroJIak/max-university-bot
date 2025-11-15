"""Главный класс скрапера, объединяющий все модули"""
from .base import BaseScraper
from .auth import AuthScraper
from .teachers import TeachersScraper
from .schedule import ScheduleScraper
from .contacts import ContactsScraper
from .personal_data import PersonalDataScraper
from .news import NewsScraper


class UniversityScraper(BaseScraper):
    """
    Главный класс скрапера для работы с сайтами университета.
    
    Объединяет функциональность всех модулей через композицию.
    """
    
    def __init__(self):
        super().__init__()
        # Создаем экземпляры всех модулей, передавая им нашу сессию
        self.auth = AuthScraper()
        self.auth.session = self.session
        self.auth.base_url = self.base_url
        self.auth.lk_base_url = self.lk_base_url
        
        self.teachers = TeachersScraper()
        self.teachers.session = self.session
        self.teachers.base_url = self.base_url
        self.teachers.lk_base_url = self.lk_base_url
        
        self.schedule = ScheduleScraper()
        self.schedule.session = self.session
        self.schedule.base_url = self.base_url
        self.schedule.lk_base_url = self.lk_base_url
        
        self.contacts = ContactsScraper()
        self.contacts.session = self.session
        self.contacts.base_url = self.base_url
        self.contacts.lk_base_url = self.lk_base_url
        
        self.personal_data = PersonalDataScraper()
        self.personal_data.session = self.session
        self.personal_data.base_url = self.base_url
        self.personal_data.lk_base_url = self.lk_base_url
        
        self.news = NewsScraper()
        self.news.session = self.session
        self.news.base_url = self.base_url
        self.news.lk_base_url = self.lk_base_url
    
    # Делегируем методы авторизации
    def login(self, email: str, password: str):
        return self.auth.login(email, password)
    
    def login_lk(self, email: str, password: str):
        return self.auth.login_lk(email, password)
    
    def login_both_sites(self, email: str, password: str):
        return self.auth.login_both_sites(email, password)
    
    # Делегируем методы работы с преподавателями
    def get_tech_page(self, cookies_json=None):
        return self.teachers.get_tech_page(cookies_json)
    
    def get_teacher_info(self, teacher_id: str, cookies_json=None):
        return self.teachers.get_teacher_info(teacher_id, cookies_json)
    
    # Делегируем методы расписания
    def get_schedule(self, date_range: str, cookies_json=None, lk_cookies_json=None):
        return self.schedule.get_schedule(date_range, cookies_json, lk_cookies_json)
    
    # Делегируем методы контактов
    def get_contacts(self, cookies_json=None):
        return self.contacts.get_contacts(cookies_json)
    
    # Делегируем методы личных данных
    def get_student_personal_data(self, cookies_json=None):
        return self.personal_data.get_student_personal_data(cookies_json)
    
    # Делегируем методы новостей
    def get_news(self, limit: int = 10, cookies_json=None):
        return self.news.get_news(limit, cookies_json)
