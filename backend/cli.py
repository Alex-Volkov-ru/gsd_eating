import logging
import click
import json

from pathlib import Path
from sqlalchemy import inspect, text

# Импортируем engine и Base
from database.create import engine, Base
from database.init import init_db
from database.models.user import User

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)  # Включаем DEBUG для диагностики
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Команды для управления базой данных"""
    pass


def _force_drop_tables():
    """Надежное удаление всех таблиц с принудительным завершением транзакций"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if not tables:
        logger.debug("Нет таблиц для удаления")
        return

    # Принудительно завершаем все активные соединения
    with engine.connect() as conn:
        conn.execute(text("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = current_database()
            AND pid <> pg_backend_pid();
        """))
        conn.commit()

    # Удаляем таблицы с явным commit
    with engine.begin() as conn:
        Base.metadata.drop_all(conn)
        logger.debug(f"Удалены таблицы: {tables}")


@click.command()
def drop():
    """Удалить все таблицы."""
    try:
        # Используем reflect для получения списка таблиц
        metadata = User.metadata
        metadata.reflect(bind=engine)

        # Удаляем таблицы в обратном порядке
        for table in reversed(metadata.sorted_tables):
            try:
                table.drop(engine)
            except Exception as drop_error:  # Указываем конкретное исключение
                logger.error(
                    f"Ошибка при удалении таблицы {table.name}: {drop_error}")
                continue  # Продолжаем удаление других таблиц

        logger.info("Таблицы удалены")
    except Exception as e:
        logger.error(f"Ошибка при удалении таблиц: {e}")


@click.command()
def create():
    """Создать таблицы в БД"""
    try:
        init_db()
        logger.info("Таблицы созданы")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise


@click.command()
def recreate():
    """Удалить и заново создать таблицы"""
    try:
        _force_drop_tables()
        init_db()
        logger.info("Таблицы пересозданы")
    except Exception as e:
        logger.error(f"Ошибка при пересоздании таблиц: {e}")
        raise


def load_json_data(file_name):
    """Загрузка JSON-файла"""
    json_path = Path(f"json/{file_name}")
    if not json_path.exists():
        logger.error(f"Файл {json_path} не найден")
        return None
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


@click.command()
def load_blood_types():
    """Загрузить типы приёмов пищи из JSON"""
    try:
        # 1. Сначала инициализируем все модели
        init_db()

        from database.models.blood_type import BloodType

        data = load_json_data("blood_type.json")
        if not data:
            logger.warning("Нет данных для загрузки")
            return

        # 3. Используем низкоуровневый SQL для очистки таблицы
        with engine.begin() as conn:
            # Очистка таблицы через SQL (избегаем ORM)
            truncate_sql = text(
                f"TRUNCATE TABLE {BloodType.__tablename__} "
                "RESTART IDENTITY CASCADE"
            )
            conn.execute(truncate_sql)

            # Добавление данных через bulk_insert_mappings
            conn.execute(
                BloodType.__table__.insert(),
                [{"id": int(k), "name": v} for k, v in data.items()]
            )

        logger.info(f"Успешно загружено {len(data)} типов приёмов")
    except Exception as e:
        logger.error(f"Ошибка при загрузке: {e}")
        raise


@click.command()
def load_meal_types():
    """Загрузить типы приёмов пищи из JSON"""
    try:
        # 1. Сначала инициализируем все модели
        init_db()

        # 2. Затем импортируем MealType отдельно
        from database.models.meal_type import MealType

        data = load_json_data("meal_type.json")
        if not data:
            logger.warning("Нет данных для загрузки")
            return

        # 3. Используем низкоуровневый SQL для очистки таблицы
        with engine.begin() as conn:
            # Очистка таблицы через SQL (избегаем ORM)
            truncate_sql = text(
                f"TRUNCATE TABLE {MealType.__tablename__} "
                "RESTART IDENTITY CASCADE"
            )
            conn.execute(truncate_sql)

            # Добавление данных через bulk_insert_mappings
            conn.execute(
                MealType.__table__.insert(),
                [{"id": int(k), "name": v} for k, v in data.items()]
            )

        logger.info(f"Успешно загружено {len(data)} типов приёмов пищи")
    except Exception as e:
        logger.error(f"Ошибка при загрузке: {e}")
        raise


@click.command()
def fill():
    """Загрузить все данные из JSON файлов"""
    commands = [
        load_meal_types,
        load_blood_types,
        # Добавьте здесь другие функции загрузки по мере необходимости
    ]

    for cmd in commands:
        try:
            # Вызываем каждую команду как функцию
            cmd.callback()
        except Exception as e:
            logger.error(f"Ошибка при выполнении {cmd.name}: {e}")
            raise


cli.add_command(create)
cli.add_command(drop)
cli.add_command(recreate)
cli.add_command(load_meal_types)
cli.add_command(load_blood_types)
cli.add_command(fill)

if __name__ == "__main__":
    cli()
