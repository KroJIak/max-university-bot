from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Используем отдельную БД для ghost-app
GHOST_DATABASE_URL = os.getenv(
    "GHOST_DATABASE_URL",
    "postgresql://maxbot:maxbot123@postgres:5432/ghost_db"
)

engine = create_engine(GHOST_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

