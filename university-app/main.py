from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.students import router as students_router
from core.database import engine, Base
import os

app = FastAPI(title="University API", version="1.0.0")

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


@app.on_event("startup")
async def startup_event():
    # Создаем базу данных если её нет
    from sqlalchemy import text
    from urllib.parse import urlparse
    
    # Получаем имя БД из URL
    db_url = os.getenv("UNIVERSITY_DATABASE_URL", "postgresql://maxbot:maxbot123@postgres:5432/university_db")
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
    
    # Создаем таблицы (checkfirst=True предотвращает ошибки если таблицы уже существуют)
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("University API service started")


@app.on_event("shutdown")
async def shutdown_event():
    print("University API service stopped")


@app.get("/")
async def root():
    return {"service": "University API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

