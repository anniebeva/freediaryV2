from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Путь к файлу базы данных SQLite
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "freediary.db")

# Создание движка SQLAlchemy для SQLite
engine = create_engine(
    f"sqlite:///{SQLITE_DB_PATH}",
    connect_args={"check_same_thread": False}  # Для SQLite в FastAPI
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания таблиц при старте
def create_tables():
    Base.metadata.create_all(bind=engine)