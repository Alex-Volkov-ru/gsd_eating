import logging

from datetime import datetime, timedelta 
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models.blood import BloodRecord
from database.models.blood_type import BloodType

logger = logging.getLogger(__name__)

def get_daily_blood_stats(user_id: int, db: Session):
    """Получает все измерения сахара за текущий день с типами"""
    try:
        today = datetime.now().date()

        records = db.query(
            BloodRecord.date_time,
            BloodType.name.label('type_name'),
            BloodRecord.glucose
        ).join(
            BloodType, BloodRecord.blood_type_id == BloodType.id
        ).filter(
            BloodRecord.user_id == user_id,
            func.date(BloodRecord.date_time) == today
        ).order_by(
            BloodRecord.date_time.desc()
        ).all()

        return records if records else None

    except Exception as e:
        logger.error(f"Ошибка при получении дневной статистики сахара: {e}")
        return None


def get_weekly_blood_stats(user_id: int, db: Session):
    """Получает все измерения сахара за последние 7 дней, отсортированные от старого к новому"""
    try:
        today = datetime.now().date()
        week_ago = today - timedelta(days=6)  # включая сегодня — 7 дней

        records = db.query(
            BloodRecord.date_time,
            BloodType.name.label('type_name'),
            BloodRecord.glucose
        ).join(
            BloodType, BloodRecord.blood_type_id == BloodType.id
        ).filter(
            BloodRecord.user_id == user_id,
            func.date(BloodRecord.date_time).between(week_ago, today)
        ).order_by(
            BloodRecord.date_time.asc()
        ).all()

        return records if records else None

    except Exception as e:
        logger.error(f"Ошибка при получении недельной статистики сахара: {e}")
        return None

def get_monthly_blood_stats(user_id: int, db: Session):
    """Получает все измерения сахара за последние 30 дней, отсортированные от старого к новому"""
    try:
        today = datetime.now().date()
        month_ago = today - timedelta(days=29)

        records = db.query(
            BloodRecord.date_time,
            BloodType.name.label('type_name'),
            BloodRecord.glucose
        ).join(
            BloodType, BloodRecord.blood_type_id == BloodType.id
        ).filter(
            BloodRecord.user_id == user_id,
            func.date(BloodRecord.date_time).between(month_ago, today)
        ).order_by(
            BloodRecord.date_time.asc()
        ).all()

        return records if records else None

    except Exception as e:
        logger.error(f"Ошибка при получении месячной статистики сахара: {e}")
        return None
