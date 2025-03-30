from sqlalchemy import inspect

from database.create import engine, Base


def check_tables():
    """Проверяет наличие таблиц в базе данных"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Таблицы в базе данных: {tables}")


def init_db():
    """Инициализирует базу данных"""
    # Импорт моделей ДОЛЖЕН быть после создания Base
    from database.models.meal_type import MealType  # noqa: F401
    from database.models.user import User  # noqa: F401
    from database.models.meal import Meal  # noqa: F401
    from database.models.blood import BloodRecord  # noqa: F401
    from database.models.blood_type import BloodType  # noqa: F401

    Base.metadata.create_all(bind=engine)
