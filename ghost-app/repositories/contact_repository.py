from sqlalchemy.orm import Session
from models.contact import Dean, Department
from typing import List


class ContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_deans(self, university_id: int) -> List[Dean]:
        """Получить все деканаты университета"""
        return self.db.query(Dean).filter(
            Dean.university_id == university_id
        ).all()

    def get_all_departments(self, university_id: int) -> List[Department]:
        """Получить все кафедры университета"""
        return self.db.query(Department).filter(
            Department.university_id == university_id
        ).all()

    def delete_all_by_university(self, university_id: int):
        """Удалить все контакты университета"""
        self.db.query(Dean).filter(Dean.university_id == university_id).delete()
        self.db.query(Department).filter(Department.university_id == university_id).delete()
        self.db.commit()

    def create_dean(self, university_id: int, **kwargs) -> Dean:
        """Создать деканат"""
        dean = Dean(university_id=university_id, **kwargs)
        self.db.add(dean)
        self.db.commit()
        self.db.refresh(dean)
        return dean

    def create_department(self, university_id: int, **kwargs) -> Department:
        """Создать кафедру"""
        department = Department(university_id=university_id, **kwargs)
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        return department

