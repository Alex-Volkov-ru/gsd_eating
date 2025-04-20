import logging

from aiogram import Router, types, F
from tabulate import tabulate
from handlers.blood_stats import escape_markdown_v2

from keyboards.keyboards import registered_kb, get_stats_main_kb, get_blood_stats_kb


router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == '📈 Статистика')
async def show_stats_menu(message: types.Message):
    try:
        await message.answer(
            "Выберите тип статистики:",
            reply_markup=get_stats_main_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка при показе меню статистики: {e}")
        await message.answer("Произошла ошибка при открытии статистики")

@router.callback_query(F.data == 'stats_back')
async def back_to_main(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
        await callback.message.answer(
            "Главное меню:",
            reply_markup=registered_kb
        )
    except Exception as e:
        logger.error(f"Ошибка при возврате в главное меню: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

@router.callback_query(F.data == 'blood_stats')
async def show_blood_menu(callback: types.CallbackQuery):
    try:
        await callback.message.edit_text(
            "Выберите период для статистики сахара:",
            reply_markup=get_blood_stats_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка при показе меню статистики сахара: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

@router.callback_query(F.data == 'blood_back')
async def back_to_stats(callback: types.CallbackQuery):
    try:
        await callback.message.edit_text(
            "Выберите тип статистики:",
            reply_markup=get_stats_main_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка при возврате в меню статистики: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

def format_blood_message(records, period_name):
    """Форматирует только список записей сахара за период — дата, время, тип, значение"""
    if not records:
        return f"📊 Нет данных за {escape_markdown_v2(period_name)}"

    message = f"📅 \\*Показатели сахара за {escape_markdown_v2(period_name)}\\*:\n\n"

    table_data = []
    for r in records:
        date_str = r['date'].strftime("%d.%m.%Y")
        time_str = r['date'].strftime("%H:%M")
        table_data.append([
            escape_markdown_v2(date_str),
            escape_markdown_v2(time_str),
            escape_markdown_v2(r['type']),
            f"{r['value']:.1f}"
        ])

    headers = ["Дата", "Время", "Тип после приема", "Уровень сахара"]
    table = tabulate(table_data, headers=headers, tablefmt="grid")

    message += f"```{table}```"
    return message