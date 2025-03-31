# flake8: noqa: F401
# Импорт моделей ДОЛЖЕН быть после создания Base
from sqlalchemy import inspect

from database.create import engine, Base


def check_tables():
    """Проверяет наличие таблиц в базе данных"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Таблицы в базе данных: {tables}")


def init_db():
    """Инициализирует базу данных"""
    from database.models.meal_type import MealType
    from database.models.user import User
    from database.models.meal import Meal
    from database.models.blood import BloodRecord
    from database.models.blood_type import BloodType

    Base.metadata.create_all(bind=engine)
