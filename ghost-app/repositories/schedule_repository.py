from sqlalchemy.orm import Session
from models.schedule import Schedule
from typing import List, Optional
from datetime import date


class ScheduleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_student_and_week(
        self,
        university_id: int,
        student_email: str,
        week: int
    ) -> List[Schedule]:
        """Получить расписание студента по неделе"""
        return self.db.query(Schedule).filter(
            Schedule.university_id == university_id,
            Schedule.student_email == student_email,
            Schedule.week == week
        ).order_by(Schedule.date, Schedule.time_start).all()

    def delete_by_student_and_week(
        self,
        university_id: int,
        student_email: str,
        week: int
    ):
        """Удалить расписание студента по неделе"""
        self.db.query(Schedule).filter(
            Schedule.university_id == university_id,
            Schedule.student_email == student_email,
            Schedule.week == week
        ).delete()
        self.db.commit()

    def create(self, university_id: int, student_email: str, **kwargs) -> Schedule:
        """Создать запись расписания"""
        schedule = Schedule(
            university_id=university_id,
            student_email=student_email,
            **kwargs
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

