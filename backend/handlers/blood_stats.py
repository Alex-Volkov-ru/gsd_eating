import logging
import re

from datetime import datetime
from aiogram import Router, types, F
from tabulate import tabulate
from sqlalchemy.orm import Session

from database.db_operations import get_daily_blood_stats
from database.create import get_db
from database.models.user import User
from keyboards.keyboards import get_blood_stats_kb

router = Router()
logger = logging.getLogger(__name__)


def get_user_from_db(db: Session, tg_id: int):
    """Получает пользователя из базы данных"""
    return db.query(User).filter(User.tg_id == tg_id).first()


def escape_markdown_v2(text: str) -> str:
    """Экранирует символы MarkdownV2"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([{}])'.format(re.escape(escape_chars)), r'\\\1', text)


@router.callback_query(F.data == 'blood_day')
async def show_daily_blood_stats(callback: types.CallbackQuery):
    """Обработчик кнопки 'Сахар за день'"""
    try:
        db = next(get_db())
        user = get_user_from_db(db, callback.from_user.id)
        
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        records = get_daily_blood_stats(user.id, db)
        
        if not records:
            await callback.message.edit_text(
                "📊 Нет данных о сахаре за сегодня",
                reply_markup=get_blood_stats_kb()
            )
            return

        # Формируем таблицу с экранированием
        table_data = []
        for record in records:
            time_str = record.date_time.strftime('%H:%M')
            glucose_str = f"{record.glucose:.1f} ммоль/л"
            
            # Экранируем только текстовые поля
            table_data.append([
                escape_markdown_v2(time_str),
                escape_markdown_v2(record.type_name),
                glucose_str  # Числовые значения не экранируем
            ])

        headers = ["Время", "Тип измерения", "Уровень сахара"]
        table = tabulate(table_data, headers, tablefmt="simple_grid")
        
        # Формируем сообщение без Markdown в таблице
        message = f"📊 Измерения сахара за {datetime.now().strftime('%d.%m.%Y')}:\n"
        message += f"<pre>{table}</pre>"

        await callback.message.edit_text(
            text=message,
            reply_markup=get_blood_stats_kb(),
            parse_mode="HTML"  # Используем HTML вместо Markdown
        )

    except Exception as e:
        logger.error(f"Ошибка при показе дневной статистики сахара: {e}")
        await callback.answer(
            "Произошла ошибка при получении статистики",
            show_alert=True
        )
    finally:
        db.close()