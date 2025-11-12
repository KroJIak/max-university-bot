from sqlalchemy.orm import Session
from models.users import User
from typing import Optional


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, first_name: str, last_name: Optional[str] = None, username: Optional[str] = None) -> User:
        db_user = User(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_user_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_by_id(self, id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def exists(self, user_id: int) -> bool:
        return self.db.query(User).filter(User.user_id == user_id).first() is not None

    def update(self, user_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None, username: Optional[str] = None) -> Optional[User]:
        """Обновить данные пользователя"""
        db_user = self.get_by_user_id(user_id)
        if not db_user:
            return None
        
        if first_name is not None:
            db_user.first_name = first_name
        if last_name is not None:
            db_user.last_name = last_name
        if username is not None:
            db_user.username = username
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        db_user = self.get_by_user_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True

