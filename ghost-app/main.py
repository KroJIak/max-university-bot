from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.students import router as students_router
from api.upload import router as upload_router
from core.database import engine, Base
import os

app = FastAPI(
    title="Ghost API",
    version="1.0.0",
    description="""
    ## Ghost API - API для симуляции University API
    
    Этот API симулирует работу University API, но использует данные из БД вместо scraping.
    Данные загружаются через CSV файлы.
    
    ### Основные возможности:
    
    * **Симуляция University API**: те же эндпоинты, что и в university-app
    * **Загрузка данных**: прием CSV файлов с данными студентов, расписаний, преподавателей и т.д.
    * **Хранение данных**: все данные хранятся в БД и возвращаются по запросам
    
    ### Использование:
    
    Ghost API активируется, если в админ панели включен функционал, но не указан endpoint.
    В этом случае администратор указывает значения вручную, а затем загружает CSV файл
    через эндпоинт `/upload`.
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

# Подключаем роутеры
app.include_router(students_router, prefix="/students", tags=["students"])
app.include_router(upload_router, tags=["upload"])  # Без prefix, так как в upload.py уже есть /upload


@app.on_event("startup")
async def startup_event():
    # Создаем базу данных если её нет
    from sqlalchemy import text
    from urllib.parse import urlparse
    
    # Получаем имя БД из URL
    db_url = os.getenv("GHOST_DATABASE_URL", "postgresql://maxbot:maxbot123@postgres:5432/ghost_db")
    parsed = urlparse(db_url)
    db_name = parsed.path.lstrip('/')
    
    # Подключаемся к postgres БД для создания новой БД
    if db_name and db_name != 'postgres':
        admin_url = db_url.rsplit('/', 1)[0] + '/postgres'
        from sqlalchemy import create_engine
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        
        try:
            with admin_engine.connect() as conn:
                # Проверяем, существует ли БД
                result = conn.execute(text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                ), {"db_name": db_name})
                
                if not result.fetchone():
                    # Создаем БД
                    conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                    print(f"Created database: {db_name}")
        except Exception as e:
            print(f"Warning: Could not create database (might already exist): {e}")
        finally:
            admin_engine.dispose()
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Ghost API service started")


@app.on_event("shutdown")
async def shutdown_event():
    print("Ghost API service stopped")


@app.get(
    "/",
    summary="Root",
    description="Возвращает информацию о сервисе Ghost API.",
    response_description="Информация о сервисе",
    responses={
        200: {"description": "Информация о сервисе"}
    }
)
async def root():
    """Root
    
    Возвращает информацию о сервисе Ghost API.
    """
    return {"service": "Ghost API", "version": "1.0.0"}


@app.get(
    "/health",
    summary="Health Check",
    description="Проверяет работоспособность API. Возвращает статус сервиса.",
    response_description="Статус сервиса",
    responses={
        200: {"description": "Сервис работает"}
    }
)
async def health():
    """Health Check
    
    Проверяет работоспособность API. Возвращает статус сервиса.
    """
    return {"status": "healthy"}

