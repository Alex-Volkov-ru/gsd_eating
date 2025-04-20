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
from database.db_operations import get_weekly_blood_stats, get_monthly_blood_stats

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
        if callback.from_user.is_bot:
            table_data = [
                [
                    record.date_time.strftime('%H:%M'),
                    record.type_name[:10],
                    f"{record.glucose:.1f}"
                ]
                for record in records
            ]
            headers = ["Время", "Тип", "Сахар"]
            table_fmt = "simple_grid"
        else:
            table_data = [
                [
                    record.date_time.strftime('%H:%M'),
                    record.type_name,
                    f"{record.glucose:.1f} ммоль/л"
                ]
                for record in records
            ]
            headers = ["Время", "Тип измерения", "Уровень сахара"]
            table_fmt = "fancy_grid"

        table = tabulate(
            table_data,
            headers=headers,
            tablefmt=table_fmt,
            stralign="center",
            numalign="center"
        )
        message = f"📊 <b>Измерения сахара за {datetime.now().strftime('%d.%m.%Y')}</b>\n"
        message += f"<pre>{table}</pre>"

        await callback.message.edit_text(
            text=message,
            reply_markup=get_blood_stats_kb(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Ошибка при показе статистики: {e}")
        await callback.answer("Ошибка при формировании отчёта", show_alert=True)
    finally:
        db.close()

@router.callback_query(F.data == 'blood_week')
async def show_weekly_blood_stats(callback: types.CallbackQuery):
    """Обработчик кнопки 'Сахар за неделю'"""
    try:
        db = next(get_db())
        user = get_user_from_db(db, callback.from_user.id)

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        records = get_weekly_blood_stats(user.id, db)

        if not records:
            await callback.message.edit_text(
                "📊 Нет данных о сахаре за последнюю неделю",
                reply_markup=get_blood_stats_kb()
            )
            return

        table_data = [
            [
                record.date_time.strftime('%d.%m %H:%M'),
                record.type_name,
                f"{record.glucose:.1f} ммоль/л"
            ]
            for record in records
        ]
        headers = ["Дата и время", "Тип измерения", "Уровень сахара"]

        table = tabulate(
            table_data,
            headers=headers,
            tablefmt="fancy_grid",
            stralign="center",
            numalign="center"
        )

        message = f"📊 <b>Измерения сахара за последнюю неделю</b>\n"
        message += f"<pre>{table}</pre>"

        await callback.message.edit_text(
            text=message,
            reply_markup=get_blood_stats_kb(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Ошибка при показе статистики за неделю: {e}")
        await callback.answer("Ошибка при формировании отчёта", show_alert=True)
    finally:
        db.close()

@router.callback_query(F.data == 'blood_month')
async def show_monthly_blood_stats(callback: types.CallbackQuery):
    """Обработчик кнопки 'Сахар за месяц' с разбивкой по неделям в виде таблиц"""
    try:
        db = next(get_db())
        user = get_user_from_db(db, callback.from_user.id)

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        records = get_monthly_blood_stats(user.id, db)

        if not records:
            await callback.message.edit_text(
                "📊 Нет данных о сахаре за последний месяц",
                reply_markup=get_blood_stats_kb()
            )
            return

        from collections import defaultdict

        # Группировка по неделям в месяце
        weeks = defaultdict(list)
        for r in records:
            # Вычисляем неделю месяца
            week_num = (r.date_time.day - 1) // 7 + 1  # делим день месяца на недели
            weeks[week_num].append(r)

        message = "<b>📊 Измерения сахара за последний месяц</b>\n\n"

        # Сортируем недели по порядку
        for week_num, week_records in sorted(weeks.items()):
            message += f"<b>🗓 Неделя {week_num}</b>\n"

            table_data = [
                [
                    r.date_time.strftime('%d.%m %H:%M'),
                    r.type_name,
                    f"{r.glucose:.1f} ммоль/л"
                ]
                for r in week_records
            ]
            headers = ["Дата и время", "Тип измерения", "Уровень сахара"]

            table = tabulate(
                table_data,
                headers=headers,
                tablefmt="fancy_grid",
                stralign="center",
                numalign="center"
            )

            message += f"<pre>{table}</pre>\n"

        await callback.message.edit_text(
            text=message.strip(),
            reply_markup=get_blood_stats_kb(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Ошибка при показе статистики за месяц: {e}")
        await callback.answer("Ошибка при формировании отчёта", show_alert=True)
    finally:
        db.close()

