from aiogram import types, F

from keyboards.keyboards import registered_kb

ABOUT_TEXT = """
<b>ℹ️ О нашем боте</b>

Этот бот создан для помощи в регулярном заборе крови после приема пищи.

Основные функции:
- ⏱ Установка напоминаний о времени забора крови
- 📊 Ведение статистики ваших замеров
- 📈 Анализ показателей в динамике

Версия: 1.0
Разработчик: Alexandr Volov
Контакты: TG @ximikat01

Для возврата в главное меню используйте кнопки ниже.
"""


async def handle_about_button(message: types.Message):
    """Обработка кнопки 'О нас'"""
    await message.answer(
        ABOUT_TEXT,
        parse_mode="HTML",
        reply_markup=registered_kb
    )


def setup_about_handlers(dp):
    """Регистрация обработчиков для раздела 'О нас'"""
    dp.message.register(handle_about_button, F.text == 'ℹ️ О нас')
