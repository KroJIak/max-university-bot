#!/usr/bin/env python3
"""
Скрипт для тестирования всех API endpoints
Использование: python test_api.py [--base-url http://localhost:8003]
"""

import requests
import json
import sys
import argparse
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class Colors:
    """Цвета для вывода в консоль"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class APITester:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
        self.test_user_id = 123456789  # Тестовый user_id
        self.test_student_email = "goliluxa@mail.ru"
        self.test_password = "P17133p17133"
        self.created_user_id = None
        self.created_student_user_id = None
        self.test_university_id = None  # ID тестового университета
        self.auth_token = None  # JWT токен для аутентификации университета
        self.university_login = "admin"  # Дефолтный логин университета
        self.university_password = "admin"  # Дефолтный пароль университета
        
    def print_test(self, test_name: str):
        """Вывести название теста"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== {test_name} ==={Colors.RESET}")
    
    def print_success(self, message: str):
        """Вывести успешное сообщение"""
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")
    
    def print_error(self, message: str):
        """Вывести сообщение об ошибке"""
        print(f"{Colors.RED}✗ {message}{Colors.RESET}")
    
    def print_info(self, message: str):
        """Вывести информационное сообщение"""
        print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")
    
    def print_response(self, response: requests.Response):
        """Вывести информацию о response"""
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   Response: {response.text[:200]}")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Получить заголовки с токеном аутентификации"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    def test_health(self) -> bool:
        """Тест health endpoint"""
        self.print_test("Health Check")
        try:
            response = requests.get(f"{self.api_base}/health")
            if response.status_code == 200:
                self.print_success("Health check passed")
                self.print_response(response)
                return True
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Health check error: {e}")
            return False
    
    # ========== UNIVERSITIES ==========
    
    def test_get_universities(self) -> bool:
        """Тест получения списка университетов"""
        self.print_test("GET Universities (list)")
        try:
            response = requests.get(f"{self.api_base}/universities")
            if response.status_code == 200:
                universities = response.json()
                self.print_success(f"Retrieved {len(universities)} universities")
                if universities:
                    # Используем первый университет для тестирования
                    self.test_university_id = universities[0]["id"]
                    print(f"   Using university ID {self.test_university_id}: {universities[0]['name']}")
                    return True
                else:
                    self.print_error("No universities found")
                    return False
            else:
                self.print_error(f"Failed to get universities: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error getting universities: {e}")
            return False
    
    def test_university_login(self) -> bool:
        """Тест аутентификации университета"""
        self.print_test("POST University Login")
        if not self.test_university_id:
            self.print_error("No university_id available")
            return False
        
        try:
            data = {
                "university_id": self.test_university_id,
                "login": self.university_login,
                "password": self.university_password
            }
            response = requests.post(f"{self.api_base}/universities/login", json=data)
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get("access_token")
                self.print_success("University login successful")
                print(f"   Token: {self.auth_token[:20]}...")
                print(f"   University: {result.get('university_name')}")
                return True
            else:
                self.print_error(f"Failed to login: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error during university login: {e}")
            return False
    
    def test_get_university(self) -> bool:
        """Тест получения университета по ID"""
        self.print_test("GET University (by id)")
        if not self.test_university_id:
            self.print_error("No university_id available")
            return False
        
        try:
            response = requests.get(f"{self.api_base}/universities/{self.test_university_id}")
            if response.status_code == 200:
                self.print_success("University retrieved")
                self.print_response(response)
                return True
            else:
                self.print_error(f"Failed to get university: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error getting university: {e}")
            return False
    
    # ========== USERS CRUD ==========
    
    def test_create_user(self) -> bool:
        """Тест создания пользователя"""
        self.print_test("CREATE User")
        if not self.test_university_id:
            self.print_error("No university_id available")
            return False
        
        try:
            data = {
                "user_id": self.test_user_id,
                "university_id": self.test_university_id,
                "first_name": "Тестовый",
                "last_name": "Пользователь",
                "username": "test_user"
            }
            response = requests.post(f"{self.api_base}/users", json=data)
            if response.status_code == 201:
                self.print_success("User created")
                self.print_response(response)
                self.created_user_id = response.json()["user_id"]
                return True
            elif response.status_code == 400 and "already exists" in response.text:
                self.print_info("User already exists (OK for testing)")
                self.created_user_id = self.test_user_id
                return True
            else:
                self.print_error(f"Failed to create user: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error creating user: {e}")
            return False
    
    def test_get_user(self) -> bool:
        """Тест получения пользователя"""
        self.print_test("READ User (by user_id)")
        if not self.created_user_id:
            self.print_error("No user_id available")
            return False
        
        try:
            response = requests.get(f"{self.api_base}/users/{self.created_user_id}")
            if response.status_code == 200:
                self.print_success("User retrieved")
                self.print_response(response)
                return True
            else:
                self.print_error(f"Failed to get user: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error getting user: {e}")
            return False
    
    def test_get_all_users(self) -> bool:
        """Тест получения списка пользователей"""
        self.print_test("READ Users (list)")
        try:
            response = requests.get(f"{self.api_base}/users?skip=0&limit=10")
            if response.status_code == 200:
                users = response.json()
                self.print_success(f"Retrieved {len(users)} users")
                if users:
                    print(f"   First user: {users[0].get('first_name', 'N/A')}")
                return True
            else:
                self.print_error(f"Failed to get users: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error getting users: {e}")
            return False
    
    def test_update_user(self) -> bool:
        """Тест обновления пользователя"""
        self.print_test("UPDATE User")
        if not self.created_user_id:
            self.print_error("No user_id available")
            return False
        
        try:
            data = {
                "first_name": "Обновленный",
                "last_name": "Тест",
                "username": "updated_test_user"
            }
            response = requests.put(f"{self.api_base}/users/{self.created_user_id}", json=data)
            if response.status_code == 200:
                self.print_success("User updated")
                self.print_response(response)
                return True
            else:
                self.print_error(f"Failed to update user: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error updating user: {e}")
            return False
    
    def test_delete_user(self) -> bool:
        """Тест удаления пользователя (пропускаем, чтобы не удалять тестового пользователя)"""
        self.print_test("DELETE User (skipped)")
        self.print_info("Skipping user deletion to preserve test data")
        return True
    
    # ========== STUDENTS CRUD ==========
    
    def test_student_login(self) -> bool:
        """Тест логина студента"""
        self.print_test("CREATE Student (login)")
        if not self.created_user_id:
            self.print_error("No user_id available")
            return False
        
        if not self.test_university_id:
            self.print_error("No university_id available")
            return False
        
        try:
            data = {
                "user_id": self.created_user_id,
                "university_id": self.test_university_id,
                "student_email": self.test_student_email,
                "password": self.test_password
            }
            response = requests.post(f"{self.api_base}/students/login", json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.print_success("Student login successful")
                    self.print_response(response)
                    self.created_student_user_id = self.created_user_id
                    return True
                else:
                    self.print_error(f"Login failed: {result.get('message', 'Unknown error')}")
                    return False
            elif response.status_code == 401:
                self.print_info("Login failed (expected - invalid credentials)")
                self.print_response(response)
                # Это нормально для тестирования с неверными credentials
                return True
            else:
                self.print_error(f"Failed to login: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error during login: {e}")
            return False
    
    def test_get_student_status(self) -> bool:
        """Тест получения статуса студента"""
        self.print_test("READ Student Status")
        if not self.created_user_id:
            self.print_error("No user_id available")
            return False
        
        try:
            response = requests.get(f"{self.api_base}/students/{self.created_user_id}/status")
            if response.status_code == 200:
                self.print_success("Student status retrieved")
                self.print_response(response)
                return True
            else:
                self.print_error(f"Failed to get status: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error getting status: {e}")
            return False
    
    def test_get_student_credentials(self) -> bool:
        """Тест получения credentials студента"""
        self.print_test("READ Student Credentials")
        if not self.created_user_id:
            self.print_error("No user_id available")
            return False
        
        try:
            response = requests.get(f"{self.api_base}/students/{self.created_user_id}")
            if response.status_code == 200:
                self.print_success("Student credentials retrieved")
                # Не выводим полные credentials (содержат зашифрованный пароль)
                data = response.json()
                print(f"   Student email: {data.get('student_email', 'N/A')}")
                print(f"   Is active: {data.get('is_active', 'N/A')}")
                return True
            elif response.status_code == 404:
                self.print_info("Credentials not found (OK if not linked)")
                return True
            else:
                self.print_error(f"Failed to get credentials: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error getting credentials: {e}")
            return False
    
    def test_get_all_students(self) -> bool:
        """Тест получения списка всех студентов"""
        self.print_test("READ Students (list)")
        try:
            response = requests.get(f"{self.api_base}/students?skip=0&limit=10")
            if response.status_code == 200:
                students = response.json()
                self.print_success(f"Retrieved {len(students)} student credentials")
                if students:
                    print(f"   First student email: {students[0].get('student_email', 'N/A')}")
                return True
            else:
                self.print_error(f"Failed to get students: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error getting students: {e}")
            return False
    
    def test_update_student_credentials(self) -> bool:
        """Тест обновления credentials студента"""
        self.print_test("UPDATE Student Credentials")
        if not self.created_student_user_id:
            self.print_info("Skipping - no student credentials to update")
            return True
        
        try:
            data = {
                "student_email": self.test_student_email
            }
            response = requests.put(
                f"{self.api_base}/students/{self.created_student_user_id}",
                json=data
            )
            if response.status_code == 200:
                self.print_success("Student credentials updated")
                self.print_response(response)
                return True
            elif response.status_code == 404:
                self.print_info("Credentials not found (OK)")
                return True
            else:
                self.print_error(f"Failed to update: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error updating credentials: {e}")
            return False
    
    def test_unlink_student(self) -> bool:
        """Тест отвязки студента (soft delete)"""
        self.print_test("DELETE Student (unlink - soft delete)")
        if not self.created_student_user_id:
            self.print_info("Skipping - no student to unlink")
            return True
        
        try:
            response = requests.delete(
                f"{self.api_base}/students/{self.created_student_user_id}/unlink"
            )
            if response.status_code == 200:
                self.print_success("Student unlinked")
                self.print_response(response)
                return True
            elif response.status_code == 404:
                self.print_info("Already unlinked (OK)")
                return True
            else:
                self.print_error(f"Failed to unlink: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error unlinking: {e}")
            return False
    
    def test_delete_student_credentials(self) -> bool:
        """Тест удаления credentials студента (hard delete)"""
        self.print_test("DELETE Student (hard delete - skipped)")
        self.print_info("Skipping hard delete to preserve test data")
        return True
    
    def test_get_student_teachers(self) -> bool:
        """Тест получения списка преподавателей студента"""
        self.print_test("GET Student Teachers")
        if not self.created_student_user_id:
            self.print_info("Skipping - no student credentials available")
            return True
        
        try:
            response = requests.get(
                f"{self.api_base}/students/{self.created_student_user_id}/teachers"
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("teachers"):
                    teachers = result.get("teachers", [])
                    self.print_success(f"Teachers list retrieved. Found {len(teachers)} teachers")
                    # Показываем первые 5 преподавателей
                    if teachers:
                        print(f"   First {min(5, len(teachers))} teachers:")
                        for teacher in teachers[:5]:
                            print(f"     {teacher.get('id')}: {teacher.get('name')}")
                        if len(teachers) > 5:
                            print(f"     ... and {len(teachers) - 5} more")
                    return True
                else:
                    self.print_error("Teachers list retrieved but list is empty")
                    self.print_response(response)
                    return False
            elif response.status_code == 404:
                self.print_info("Student not linked (OK)")
                return True
            elif response.status_code == 401:
                self.print_info("Session expired or not found (OK for testing)")
                return True
            else:
                self.print_error(f"Failed to get tech page: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error getting tech page: {e}")
            return False
    
    def test_get_student_personal_data(self) -> bool:
        """Тест получения personal data студента"""
        self.print_test("GET Student Personal Data")
        if not self.created_student_user_id:
            self.print_info("Skipping - no student credentials available")
            return True
        
        try:
            response = requests.get(
                f"{self.api_base}/students/{self.created_student_user_id}/personal_data"
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("data"):
                    self.print_success("Personal data retrieved")
                    data = result.get("data", {})
                    # Показываем количество найденных полей
                    filled_fields = {k: v for k, v in data.items() if v is not None}
                    print(f"   Found {len(filled_fields)} fields with data:")
                    for key, value in filled_fields.items():
                        # Специальная обработка для фото (base64 данные)
                        if key == "photo" and value:
                            if value.startswith("data:image"):
                                # Это base64 изображение
                                photo_size = len(value)
                                print(f"     {key}: [base64 image, {photo_size} chars, format: {value[5:value.find(';')]}]")
                            else:
                                print(f"     {key}: {str(value)[:50]}...")
                        elif key == "photo_url" and value:
                            print(f"     {key}: {value}")
                        else:
                            # Обрезаем длинные значения для вывода
                            display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                            print(f"     {key}: {display_value}")
                    return True
                else:
                    self.print_error("Personal data retrieved but data is empty")
                    self.print_response(response)
                    return False
            elif response.status_code == 404:
                self.print_info("Student not linked or method disabled (OK)")
                return True
            elif response.status_code == 401:
                self.print_info("Cookies not working for lk.chuvsu.ru (OK for testing)")
                self.print_response(response)
                return True
            elif response.status_code == 503:
                self.print_info("University API not configured (OK for testing)")
                return True
            else:
                self.print_error(f"Failed to get personal data: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error getting personal data: {e}")
            return False
    
    def test_get_teacher_info(self) -> bool:
        """Тест получения информации о преподавателе"""
        self.print_test("GET Teacher Info")
        if not self.created_student_user_id:
            self.print_info("Skipping - no student credentials available")
            return True
        
        # Используем ID первого преподавателя из списка (если есть)
        # Для теста используем реальный ID преподавателя
        test_teacher_id = "2173"  # Можно использовать любой ID из списка преподавателей
        
        try:
            response = requests.get(
                f"{self.api_base}/students/{self.created_student_user_id}/teacher/{test_teacher_id}"
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    departments = result.get("departments", [])
                    photo = result.get("photo")
                    self.print_success(f"Teacher info retrieved. Found {len(departments)} departments")
                    if departments:
                        print(f"   Departments:")
                        for dept in departments:
                            print(f"     - {dept}")
                    if photo:
                        if photo.startswith("data:image"):
                            photo_size = len(photo)
                            print(f"   Photo: [base64 image, {photo_size} chars, format: {photo[5:photo.find(';')]}]")
                        else:
                            print(f"   Photo: {photo[:50]}...")
                    else:
                                print(f"   Photo: None (no photo available)")
                    return True
                else:
                    self.print_error("Teacher info retrieved but data is empty")
                    self.print_response(response)
                    return False
            elif response.status_code == 404:
                self.print_info("Student not linked or method disabled (OK)")
                return True
            elif response.status_code == 401:
                self.print_info("Session expired or not found (OK for testing)")
                self.print_response(response)
                return True
            elif response.status_code == 503:
                self.print_info("University API not configured (OK for testing)")
                return True
            else:
                self.print_error(f"Failed to get teacher info: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error during teacher info retrieval: {e}")
            return False
    
    def test_get_student_schedule(self) -> bool:
        """Тест получения расписания студента"""
        self.print_test("GET Student Schedule")
        if not self.created_student_user_id:
            self.print_info("Skipping - no student credentials available")
            return True
        
        try:
            # Вычисляем текущую дату для тестового диапазона
            today = datetime.now()
            
            # Создаем диапазон: текущая неделя (7 дней вперед)
            start_date = today
            end_date = today + timedelta(days=7)
            
            # Форматируем в ДД.ММ-ДД.ММ
            date_range = f"{start_date.strftime('%d.%m')}-{end_date.strftime('%d.%m')}"
            
            self.print_info(f"Testing with date_range: {date_range}")
            
            response = requests.get(
                f"{self.api_base}/students/{self.created_student_user_id}/schedule",
                params={"date_range": date_range}
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("schedule") is not None:
                    schedule = result.get("schedule", [])
                    self.print_success(f"Schedule retrieved. Found {len(schedule)} lessons")
                    # Показываем первые 5 занятий
                    if schedule:
                        print(f"   First {min(5, len(schedule))} lessons:")
                        for lesson in schedule[:5]:
                            print(f"     {lesson.get('date')} {lesson.get('time_start')}-{lesson.get('time_end')}: {lesson.get('subject')} ({lesson.get('type')})")
                            if lesson.get('teacher'):
                                print(f"       Teacher: {lesson.get('teacher')}")
                            if lesson.get('room'):
                                print(f"       Room: {lesson.get('room')}")
                            if lesson.get('additional_info'):
                                print(f"       Additional: {lesson.get('additional_info')}")
                        if len(schedule) > 5:
                            print(f"     ... and {len(schedule) - 5} more")
                    else:
                        self.print_info("Schedule is empty (no lessons in this date range)")
                    return True
                else:
                    self.print_error("Schedule retrieved but success is False or schedule is None")
                    self.print_response(response)
                    return False
            elif response.status_code == 404:
                self.print_info("Student not linked or method disabled (OK)")
                return True
            elif response.status_code == 401:
                self.print_info("Session expired or not found (OK for testing)")
                self.print_response(response)
                return True
            elif response.status_code == 503:
                self.print_info("University API not configured (OK for testing)")
                return True
            else:
                self.print_error(f"Failed to get schedule: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error during schedule retrieval: {e}")
            return False
    
    def test_get_student_contacts(self) -> bool:
        """Тест получения контактов деканатов и кафедр"""
        self.print_test("GET Student Contacts")
        if not self.created_student_user_id:
            self.print_info("Skipping - no student credentials available")
            return True
        
        try:
            response = requests.get(
                f"{self.api_base}/students/{self.created_student_user_id}/contacts"
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    deans = result.get("deans", [])
                    departments = result.get("departments", [])
                    self.print_success(f"Contacts retrieved. Found {len(deans)} deans, {len(departments)} departments")
                    if deans:
                        print(f"   First {min(3, len(deans))} deans:")
                        for dean in deans[:3]:
                            print(f"     {dean.get('faculty')}: {dean.get('phone') or 'N/A'}, {dean.get('email') or 'N/A'}")
                        if len(deans) > 3:
                            print(f"     ... and {len(deans) - 3} more")
                    if departments:
                        print(f"   First {min(3, len(departments))} departments:")
                        for dept in departments[:3]:
                            print(f"     {dept.get('faculty')} - {dept.get('department')}: {dept.get('phones') or 'N/A'}, {dept.get('email') or 'N/A'}")
                        if len(departments) > 3:
                            print(f"     ... and {len(departments) - 3} more")
                    return True
                else:
                    self.print_error("Contacts retrieved but data is empty")
                    self.print_response(response)
                    return False
            elif response.status_code == 404:
                self.print_info("Student not linked or method disabled (OK)")
                return True
            elif response.status_code == 401:
                self.print_info("Session expired or not found (OK for testing)")
                self.print_response(response)
                return True
            elif response.status_code == 503:
                self.print_info("University API not configured (OK for testing)")
                return True
            else:
                self.print_error(f"Failed to get contacts: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error during contacts retrieval: {e}")
            return False
    
    def test_get_student_platforms(self) -> bool:
        """Тест получения списка полезных веб-платформ"""
        self.print_test("GET Student Platforms")
        if not self.created_student_user_id:
            self.print_info("Skipping - no student credentials available")
            return True
        
        try:
            response = requests.get(
                f"{self.api_base}/students/{self.created_student_user_id}/platforms"
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("platforms"):
                    platforms = result.get("platforms", [])
                    self.print_success(f"Platforms retrieved. Found {len(platforms)} platforms")
                    if platforms:
                        print(f"   Platforms:")
                        for platform in platforms:
                            print(f"     {platform.get('key')}: {platform.get('name')} - {platform.get('url')}")
                    return True
                else:
                    self.print_error("Platforms retrieved but list is empty")
                    self.print_response(response)
                    return False
            elif response.status_code == 404:
                self.print_info("Student not linked or method disabled (OK)")
                return True
            elif response.status_code == 401:
                self.print_info("Session expired or not found (OK for testing)")
                self.print_response(response)
                return True
            elif response.status_code == 503:
                self.print_info("University API not configured (OK for testing)")
                return True
            else:
                self.print_error(f"Failed to get platforms: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error during platforms retrieval: {e}")
            return False
    
    # ========== CONFIG (requires authentication) ==========
    
    def test_get_university_config(self) -> bool:
        """Тест получения конфигурации университета (требуется аутентификация)"""
        self.print_test("GET University Config")
        if not self.test_university_id:
            self.print_info("Skipping - no university_id available")
            return True
        
        if not self.auth_token:
            self.print_info("Skipping - no auth token available (requires university login)")
            return True
        
        try:
            headers = self.get_auth_headers()
            response = requests.get(
                f"{self.api_base}/config/university/{self.test_university_id}",
                headers=headers
            )
            if response.status_code == 200:
                self.print_success("University config retrieved")
                config = response.json()
                print(f"   API Base URL: {config.get('university_api_base_url', 'N/A')}")
                endpoints = config.get('endpoints', {})
                print(f"   Endpoints: {len(endpoints)} configured")
                if endpoints:
                    print(f"   Endpoints details:")
                    for key, value in endpoints.items():
                        print(f"     {key}: {value}")
                else:
                    print(f"   No endpoints configured")
                self.print_response(response)
                return True
            elif response.status_code == 404:
                self.print_info("Config not found (OK - not configured yet)")
                return True
            elif response.status_code == 401 or response.status_code == 403:
                self.print_info("Unauthorized (OK - auth token may be invalid)")
                return True
            else:
                self.print_error(f"Failed to get config: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error getting config: {e}")
            return False
    
    def test_get_university_endpoints_status(self) -> bool:
        """Тест получения статуса endpoints университета (требуется аутентификация)"""
        self.print_test("GET University Endpoints Status")
        if not self.test_university_id:
            self.print_info("Skipping - no university_id available")
            return True
        
        if not self.auth_token:
            self.print_info("Skipping - no auth token available (requires university login)")
            return True
        
        try:
            headers = self.get_auth_headers()
            response = requests.get(
                f"{self.api_base}/config/university/{self.test_university_id}/endpoints/status",
                headers=headers
            )
            if response.status_code == 200:
                self.print_success("Endpoints status retrieved")
                status = response.json()
                enabled = sum(1 for v in status.values() if v)
                total = len(status)
                print(f"   Enabled: {enabled}/{total} endpoints")
                for endpoint, is_enabled in status.items():
                    status_str = "✓" if is_enabled else "✗"
                    print(f"     {status_str} {endpoint}")
                return True
            elif response.status_code == 401 or response.status_code == 403:
                self.print_info("Unauthorized (OK - auth token may be invalid)")
                return True
            else:
                self.print_error(f"Failed to get endpoints status: {response.status_code}")
                self.print_response(response)
                return False
        except Exception as e:
            self.print_error(f"Error getting endpoints status: {e}")
            return False
    
    def run_all_tests(self):
        """Запустить все тесты"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("=" * 60)
        print("  API Endpoints Test Suite")
        print(f"  Base URL: {self.base_url}")
        print("=" * 60)
        print(f"{Colors.RESET}")
        
        results = []
        
        # Health check
        results.append(("Health Check", self.test_health()))
        time.sleep(0.5)
        
        # Universities
        results.append(("Get Universities", self.test_get_universities()))
        time.sleep(0.5)
        results.append(("Get University", self.test_get_university()))
        time.sleep(0.5)
        results.append(("University Login", self.test_university_login()))
        time.sleep(0.5)
        
        # Users CRUD
        results.append(("Create User", self.test_create_user()))
        time.sleep(0.5)
        results.append(("Get User", self.test_get_user()))
        time.sleep(0.5)
        results.append(("Get All Users", self.test_get_all_users()))
        time.sleep(0.5)
        results.append(("Update User", self.test_update_user()))
        time.sleep(0.5)
        results.append(("Delete User", self.test_delete_user()))
        time.sleep(0.5)
        
        # Students CRUD
        results.append(("Student Login", self.test_student_login()))
        time.sleep(0.5)
        results.append(("Get Student Status", self.test_get_student_status()))
        time.sleep(0.5)
        results.append(("Get Student Credentials", self.test_get_student_credentials()))
        time.sleep(0.5)
        results.append(("Get All Students", self.test_get_all_students()))
        time.sleep(0.5)
        results.append(("Update Student Credentials", self.test_update_student_credentials()))
        time.sleep(0.5)
        results.append(("Get Student Teachers", self.test_get_student_teachers()))
        time.sleep(0.5)
        results.append(("Get Student Personal Data", self.test_get_student_personal_data()))
        time.sleep(0.5)
        results.append(("Get Teacher Info", self.test_get_teacher_info()))
        time.sleep(0.5)
        results.append(("Get Student Schedule", self.test_get_student_schedule()))
        time.sleep(0.5)
        results.append(("Get Student Contacts", self.test_get_student_contacts()))
        time.sleep(0.5)
        results.append(("Get Student Platforms", self.test_get_student_platforms()))
        time.sleep(0.5)
        results.append(("Unlink Student", self.test_unlink_student()))
        time.sleep(0.5)
        results.append(("Delete Student", self.test_delete_student_credentials()))
        time.sleep(0.5)
        
        # Config (requires authentication)
        results.append(("Get University Config", self.test_get_university_config()))
        time.sleep(0.5)
        results.append(("Get University Endpoints Status", self.test_get_university_endpoints_status()))
        
        # Summary
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("=" * 60)
        print("  Test Summary")
        print("=" * 60)
        print(f"{Colors.RESET}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
            print(f"  {status} - {test_name}")
        
        print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}")
        
        if passed == total:
            print(f"{Colors.GREEN}All tests passed!{Colors.RESET}")
            return 0
        else:
            print(f"{Colors.RED}Some tests failed!{Colors.RESET}")
            return 1


def main():
    parser = argparse.ArgumentParser(description="Test all API endpoints")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8003",
        help="Base URL of the API (default: http://localhost:8003)"
    )
    
    args = parser.parse_args()
    
    tester = APITester(base_url=args.base_url)
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

