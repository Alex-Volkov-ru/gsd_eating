import logging

from aiogram import Router, types, F

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

def format_blood_message(stats, period_name):
    """Форматирует статистику в читаемое сообщение"""
    if not stats:
        return f"Нет данных за {period_name}"
    
    message = f"📊 Статистика сахара за {period_name}:\n\n"
    message += f"• Средний уровень: {stats.get('avg', 0):.1f} ммоль/л\n"
    message += f"• Минимальный: {stats.get('min', 0):.1f} ммоль/л\n"
    message += f"• Максимальный: {stats.get('max', 0):.1f} ммоль/л\n"
    message += f"• Всего измерений: {stats.get('count', 0)}\n"

    if 'records' in stats:
        message += "\nПоследние измерения:\n"
        for record in stats['records']:
            message += f"→ {record['time']} - {record['value']:.1f} ммоль/л\n"
    
    return message