import logging
from aiogram import Router, types, F
from sqlalchemy.orm import Session

from database.db_operations import get_daily_blood_stats
from database.create import get_db
from database.models.user import User
from handlers.stats_handler import format_blood_message
from keyboards.keyboards import get_blood_stats_kb

router = Router()
logger = logging.getLogger(__name__)

async def get_user_from_db(tg_id: int, db: Session):
    """Асинхронно получает пользователя из базы данных"""
    return db.query(User).filter(User.tg_id == tg_id).first()

@router.callback_query(F.data == 'blood_day')
async def show_daily_blood_stats(callback: types.CallbackQuery):
    try:
        db = next(get_db())
        user = await get_user_from_db(callback.from_user.id, db)

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        records = get_daily_blood_stats(user.id, db)

        if not records:
            await callback.message.edit_text(
                "Нет данных о сахаре за сегодня",
                reply_markup=get_blood_stats_kb()
            )
            return

        message = format_blood_message(records, "сегодня")
        await callback.message.edit_text(
            text=message,
            reply_markup=get_blood_stats_kb(),
            parse_mode="MarkdownV2"
        )

    except Exception as e:
        logger.error(f"Ошибка при показе дневной статистики сахара: {e}")
        await callback.answer(
            "Произошла ошибка при получении статистики",
            show_alert=True
        )
    finally:
        db.close()
