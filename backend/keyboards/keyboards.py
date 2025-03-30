from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Для незарегистрированных
unregistered_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📝 Регистрация')],
        [KeyboardButton(text='❓ Помощь')],
    ],
    resize_keyboard=True
)

# Для зарегистрированных
registered_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='⏱ Запустить таймер')],
        [KeyboardButton(text='📊 Внести данные'),
         KeyboardButton(text='📈 Статистика')],
        [KeyboardButton(text='ℹ️ О нас')],
    ],
    resize_keyboard=True
)

timer_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Старт')],
        [KeyboardButton(text='Стоп')],
        [KeyboardButton(text='⬅ Назад')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)
