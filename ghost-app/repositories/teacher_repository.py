from sqlalchemy.orm import Session
from models.teacher import Teacher
from typing import List, Optional


class TeacherRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_university(self, university_id: int) -> List[Teacher]:
        """Получить всех преподавателей университета"""
        return self.db.query(Teacher).filter(
            Teacher.university_id == university_id
        ).all()

    def get_by_id(self, university_id: int, teacher_id: str) -> Optional[Teacher]:
        """Получить преподавателя по ID"""
        return self.db.query(Teacher).filter(
            Teacher.university_id == university_id,
            Teacher.teacher_id == teacher_id
        ).first()

    def create_or_update(self, university_id: int, teacher_id: str, **kwargs) -> Teacher:
        """Создать или обновить преподавателя"""
        teacher = self.get_by_id(university_id, teacher_id)
        if teacher:
            for key, value in kwargs.items():
                if hasattr(teacher, key) and value is not None:
                    setattr(teacher, key, value)
        else:
            teacher = Teacher(
                university_id=university_id,
                teacher_id=teacher_id,
                **kwargs
            )
            self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

