from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from api.v1 import health, users, config, proxy, universities
# Импортируем модели для создания таблиц
from models import University, User, Message, StudentCredentials, UniversityConfig

# Создаем таблицы (checkfirst=True предотвращает ошибки, если таблицы уже существуют)
Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title="MAX Bot API",
    version="1.0.0",
    description="""
    ## MAX Bot API - API для управления ботом университета
    
    Этот API предоставляет endpoints для управления пользователями, университетами,
    студентами и их данными.
    
    ### Основные возможности:
    
    * **Управление университетами**: создание, получение, обновление и удаление университетов
    * **Аутентификация университетов**: логин и получение JWT токенов для доступа к защищенным endpoints
    * **Управление пользователями**: CRUD операции для пользователей системы MAX
    * **Управление студентами**: привязка аккаунтов студентов, получение данных студентов
    * **Конфигурация University API**: настройка endpoints для различных функций университета
    * **Получение данных студентов**: расписание, преподаватели, контакты, платформы и т.д.
    * **Карты корпусов**: получение списка корпусов с координатами и ссылками на карты (Яндекс, 2ГИС, Google)
    
    ### Аутентификация
    
    Для доступа к защищенным endpoints (конфигурация) требуется аутентификация через JWT токен.
    Получите токен через endpoint `/api/v1/universities/login` и используйте его в заголовке:
    `Authorization: Bearer <token>`
    
    ### Multi-tenancy
    
    Система поддерживает multi-tenancy: каждый университет имеет свою конфигурацию
    и данные изолированы по `university_id`.
    """,
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры Main API
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(universities.router, prefix="/api/v1", tags=["universities"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(proxy.router, prefix="/api/v1", tags=["students"])


@app.on_event("startup")
async def startup_event():
    """Инициализация приложения при запуске"""
    from core.database import SessionLocal
    from repositories.university_repository import UniversityRepository
    
    # Создаем тестовые университеты, если их нет
    db = SessionLocal()
    try:
        university_repo = UniversityRepository(db)
        
        # Проверяем, есть ли уже университеты
        existing_universities = university_repo.get_all(limit=1000)
        if not existing_universities:
            # Создаем 3 тестовых университета
            test_universities = [
                "Чувашский государственный университет",
                "Московский государственный университет",
                "Санкт-Петербургский государственный университет"
            ]
            
            for university_name in test_universities:
                try:
                    university_repo.create(name=university_name, login="admin", password="admin")
                    print(f"Создан тестовый университет: {university_name} (login: admin, password: admin)")
                except Exception as e:
                    print(f"Ошибка при создании университета {university_name}: {e}")
        else:
            # Обновляем существующие университеты: устанавливаем дефолтные логин и пароль, если их нет
            from sqlalchemy import text
            for university in existing_universities:
                try:
                    # Проверяем, есть ли у университета пароль (проверяем через БД напрямую)
                    # Используем raw SQL для проверки, так как модель может не иметь этих полей после миграции
                    result = db.execute(text(
                        "SELECT login, password_hash FROM universities WHERE id = :id"
                    ), {"id": university.id}).fetchone()
                    
                    if result:
                        db_login, db_password_hash = result
                        # Если пароля нет или он NULL, устанавливаем дефолтные логин и пароль
                        if not db_password_hash or db_password_hash == '' or db_password_hash is None:
                            university_repo.update(
                                id=university.id,
                                login="admin",
                                password="admin"
                            )
                            print(f"✅ Обновлен университет {university.name} (ID: {university.id}): установлены логин и пароль (admin/admin)")
                        elif not db_login or db_login == '' or db_login is None:
                            # Устанавливаем дефолтный логин
                            university_repo.update(
                                id=university.id,
                                login="admin"
                            )
                            print(f"✅ Обновлен университет {university.name} (ID: {university.id}): установлен логин (admin)")
                        else:
                            print(f"ℹ️  Университет {university.name} (ID: {university.id}): логин и пароль уже установлены")
                    else:
                        # Если результат не найден, устанавливаем дефолтные логин и пароль
                        university_repo.update(
                            id=university.id,
                            login="admin",
                            password="admin"
                        )
                        print(f"✅ Обновлен университет {university.name} (ID: {university.id}): установлены логин и пароль (admin/admin)")
                except Exception as e:
                    print(f"❌ Ошибка при обновлении университета {university.name} (ID: {university.id}): {e}")
                    import traceback
                    print(f"Трассировка: {traceback.format_exc()}")
        
        print("FastAPI service started")
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI service stopped")

