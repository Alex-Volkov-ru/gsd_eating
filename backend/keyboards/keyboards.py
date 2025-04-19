from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

def get_data_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🍎 Внести данные по еде')],
            [KeyboardButton(text='🩸 Внести показатели сахара в крови')],
            [KeyboardButton(text='⬅ Назад')]
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню...'
    )


def get_stats_main_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🩸 Показатели сахара', callback_data='blood_stats')],
            [InlineKeyboardButton(text='🍎 Статистика по еде', callback_data='food_stats')],
            [InlineKeyboardButton(text='⬅ Назад', callback_data='stats_back')]
        ]
    )

def get_blood_stats_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📊 Сахар за день', callback_data='blood_day')],
            [InlineKeyboardButton(text='📈 Сахар за неделю', callback_data='blood_week')],
            [InlineKeyboardButton(text='📉 Сахар за месяц', callback_data='blood_month')],
            [InlineKeyboardButton(text='🔎 Фильтр по датам', callback_data='blood_filter')],
            [InlineKeyboardButton(text='⬅ Назад', callback_data='blood_back')]
        ]
    )