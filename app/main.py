from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from api.v1 import health, users, config, proxy
# Импортируем модели для создания таблиц
from models import User, Message, StudentCredentials, UniversityConfig

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MAX Bot API", version="1.0.0")

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
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(proxy.router, prefix="/api/v1", tags=["students"])


@app.on_event("startup")
async def startup_event():
    print("FastAPI service started")


@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI service stopped")

