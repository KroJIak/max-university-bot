from sqlalchemy.orm import Session
from models.session_cookies import SessionCookies
from typing import Optional
from datetime import datetime


class SessionCookiesRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update(
        self,
        student_email: str,
        cookies_by_domain: str  # JSON строка
    ) -> SessionCookies:
        """Создать или обновить cookies для email"""
        existing = self.db.query(SessionCookies).filter(
            SessionCookies.student_email == student_email
        ).first()
        
        if existing:
            existing.cookies_by_domain = cookies_by_domain
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            session_cookies = SessionCookies(
                student_email=student_email,
                cookies_by_domain=cookies_by_domain
            )
            self.db.add(session_cookies)
            self.db.commit()
            self.db.refresh(session_cookies)
            return session_cookies

    def get_by_email(self, student_email: str) -> Optional[SessionCookies]:
        """Получить cookies по email"""
        return self.db.query(SessionCookies).filter(
            SessionCookies.student_email == student_email
        ).first()

    def update_last_used(self, student_email: str) -> bool:
        """Обновить время последнего использования"""
        session_cookies = self.get_by_email(student_email)
        if not session_cookies:
            return False
        
        session_cookies.last_used_at = datetime.utcnow()
        self.db.commit()
        return True

    def delete(self, student_email: str) -> bool:
        """Удалить cookies по email"""
        session_cookies = self.get_by_email(student_email)
        if not session_cookies:
            return False
        
        self.db.delete(session_cookies)
        self.db.commit()
        return True

