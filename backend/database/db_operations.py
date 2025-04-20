import logging
import re
from datetime import datetime
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from database.models.blood import BloodRecord
from database.models.blood_type import BloodType
from database.models.user import User

logger = logging.getLogger(__name__)



def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for proper rendering in MarkdownV2."""
    # Список символов, которые нужно экранировать
    escape_chars = r'_*[]()~`>#+-=|{}.!'

    # Экранируем все специальные символы
    text = re.sub(r'([{}])'.format(re.escape(escape_chars)), r'\\\1', text)

    return text


def get_daily_blood_stats(user_id: int, db: Session):
    """Получает список всех записей сахара за день"""
    try:
        today = datetime.now().date()

        records = db.query(
            BloodRecord.glucose,
            BloodRecord.date_time,
            BloodType.name.label("type")
        ).join(BloodType, BloodRecord.blood_type_id == BloodType.id).filter(
            BloodRecord.user_id == user_id,
            func.date(BloodRecord.date_time) == today
        ).order_by(
            BloodRecord.date_time.desc()
        ).all()

        formatted = [{
            'value': r.glucose,
            'date': r.date_time,
            'type': r.type  # ← уже безопасно обращаться к типу
        } for r in records]

        return formatted

    except Exception as e:
        logger.error(f"Ошибка при получении дневных записей сахара: {e}")
        return []
