import os
import logging

from tenacity import (
    retry, wait_fixed,
    stop_after_attempt,
    retry_if_exception_type)
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Строка подключения к PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

# Базовый класс для моделей
Base = declarative_base()


# Функция для повторного подключения
@retry(
    wait=wait_fixed(10),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(OperationalError),
    before_sleep=lambda retry_state: logger.warning(
        f"Повторная попытка подключения: {retry_state.attempt_number}"),
)
def connect_to_db():
    """Подключается к базе данных с повторными попытками"""
    logger.debug("Попытка подключения к базе данных...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        logger.debug("Успешное подключение!")
        result = connection.execute(text("SELECT 1"))
        logger.debug(f"Результат: {result.fetchone()}")
    return engine


def get_sessionmaker(engine):
    """Создает фабрику сессий"""
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )


# Инициализация подключения
try:
    engine = connect_to_db()
    SessionLocal = get_sessionmaker(engine)
except Exception as e:
    logger.error(f"Произошла ошибка: {str(e)}")
    raise


def get_db():
    """Генератор сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
