from sqlalchemy.orm import Session
from models.student_credentials import StudentCredentials
from typing import Optional


class StudentCredentialsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        student_email: str,
    ) -> StudentCredentials:
        """Создать новую связь пользователя с аккаунтом студента"""
        db_credential = StudentCredentials(
            user_id=user_id,
            student_email=student_email,
            is_active=True,
        )
        self.db.add(db_credential)
        self.db.commit()
        self.db.refresh(db_credential)
        return db_credential

    def get_by_user_id(self, user_id: int) -> Optional[StudentCredentials]:
        """Получить активные credentials по user_id"""
        return self.db.query(StudentCredentials).filter(
            StudentCredentials.user_id == user_id,
            StudentCredentials.is_active == True
        ).first()
    
    def get_by_user_id_any(self, user_id: int) -> Optional[StudentCredentials]:
        """Получить credentials по user_id (включая неактивные)"""
        return self.db.query(StudentCredentials).filter(
            StudentCredentials.user_id == user_id
        ).first()

    def get_by_email(self, student_email: str) -> Optional[StudentCredentials]:
        """Получить credentials по email студента"""
        return self.db.query(StudentCredentials).filter(
            StudentCredentials.student_email == student_email,
            StudentCredentials.is_active == True
        ).first()

    def update(
        self,
        user_id: int,
        student_email: Optional[str] = None,
    ) -> Optional[StudentCredentials]:
        """Обновить данные credentials"""
        db_credential = self.get_by_user_id(user_id)
        if not db_credential:
            return None
        
        if student_email is not None:
            db_credential.student_email = student_email
        
        self.db.commit()
        self.db.refresh(db_credential)
        return db_credential

    def get_all(self, skip: int = 0, limit: int = 100) -> list[StudentCredentials]:
        """Получить все активные credentials"""
        return self.db.query(StudentCredentials).filter(
            StudentCredentials.is_active == True
        ).offset(skip).limit(limit).all()

    def deactivate(self, user_id: int) -> bool:
        """Деактивировать связь (мягкое удаление)"""
        db_credential = self.get_by_user_id(user_id)
        if not db_credential:
            return False
        
        db_credential.is_active = False
        self.db.commit()
        return True

    def delete(self, user_id: int) -> bool:
        """Полностью удалить связь из БД"""
        db_credential = self.get_by_user_id(user_id)
        if not db_credential:
            return False
        
        self.db.delete(db_credential)
        self.db.commit()
        return True

    def exists(self, user_id: int) -> bool:
        """Проверить, существует ли активная связь для пользователя"""
        return self.get_by_user_id(user_id) is not None

