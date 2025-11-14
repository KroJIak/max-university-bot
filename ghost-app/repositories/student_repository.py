from sqlalchemy.orm import Session
from models.student import Student
from typing import Optional


class StudentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, university_id: int, student_email: str) -> Optional[Student]:
        """Получить студента по email и university_id"""
        return self.db.query(Student).filter(
            Student.university_id == university_id,
            Student.student_email == student_email
        ).first()

    def create_or_update(self, university_id: int, student_email: str, **kwargs) -> Student:
        """Создать или обновить студента"""
        student = self.get_by_email(university_id, student_email)
        if student:
            for key, value in kwargs.items():
                if hasattr(student, key) and value is not None:
                    setattr(student, key, value)
        else:
            student = Student(
                university_id=university_id,
                student_email=student_email,
                **kwargs
            )
            self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

