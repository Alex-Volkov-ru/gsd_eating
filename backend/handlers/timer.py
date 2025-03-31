import logging
import asyncio

from datetime import datetime, timedelta
from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

from keyboards.keyboards import timer_kb, registered_kb

scheduler = AsyncIOScheduler()
active_timers = {}  # {chat_id: job}
stop_spam_flags = {}  # {chat_id: True/False}

REMINDER_INTERVAL = 1  # Интервал отправки сообщений (сек)
REMINDER_DURATION = 30  # Длительность спама (сек)


class TimerStates(StatesGroup):
    waiting_for_meal_time = State()
    waiting_for_reminder_minutes = State()


async def handle_timer_button(message: types.Message):
    """Обработка кнопки запуска таймера"""
    await message.answer("Управление таймером:", reply_markup=timer_kb)


async def handle_start_button(message: types.Message, state: FSMContext):
    """Начало работы с таймером"""
    await message.answer(
        "Введите время приема пищи (HH:MM):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(TimerStates.waiting_for_meal_time)


async def process_meal_time(message: types.Message, state: FSMContext):
    """Обработка введенного времени"""
    try:
        hours, minutes = map(int, message.text.split(':'))
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError

        await state.update_data(meal_time=message.text)
        await message.answer(
            "Через сколько минут напомнить?",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(TimerStates.waiting_for_reminder_minutes)
    except ValueError:
        await message.answer(
            "❌ Неверный формат времени. Используйте HH:MM",
            reply_markup=timer_kb)


async def process_reminder_minutes(message: types.Message, state: FSMContext):
    """Обработка интервала напоминания"""
    try:
        minutes = int(message.text)
        if minutes <= 0:
            raise ValueError

        user_data = await state.get_data()
        meal_time = user_data['meal_time']
        hours, mins = map(int, meal_time.split(':'))

        reminder_time = datetime.now().replace(
            hour=hours, minute=mins, second=0) + timedelta(minutes=minutes)

        # Отмена предыдущего таймера
        if message.chat.id in active_timers:
            active_timers[message.chat.id].remove()

        # Запуск нового таймера
        job = scheduler.add_job(
            send_repeated_reminders,
            'date',
            run_date=reminder_time,
            args=[message.chat.id, message.bot]
        )
        active_timers[message.chat.id] = job
        stop_spam_flags[message.chat.id] = False  # Флаг для спама

        await message.answer(
            "✅ Напоминание будет каждую секунду "
            f" с {reminder_time.strftime('%H:%M')} в течение 30 секунд!",
            reply_markup=registered_kb
        )
        await state.clear()
    except ValueError:
        await message.answer(
            "❌ Введите положительное число минут", reply_markup=timer_kb)


async def send_repeated_reminders(chat_id: int, bot: Bot):
    """Отправляет повторяющиеся напоминания каждые
    секунду в течение 30 секунд."""
    logging.info(f"Запуск напоминаний для пользователя {chat_id}.")
    start_time = datetime.now()

    while (datetime.now() - start_time).seconds < REMINDER_DURATION:
        if stop_spam_flags.get(chat_id, False):  # Проверка флага на остановку
            logging.info(f"Спам остановлен для {chat_id}.")
            break

        try:
            await bot.send_message(
                chat_id, "⏰ Время сделать забор крови!",
                reply_markup=timer_kb  # ОСТАВЛЯЕМ timer_kb ВО ВРЕМЯ СПАМА!
            )
            logging.info(f"Напоминание отправлено пользователю {chat_id}.")
        except Exception as e:
            logging.error(f"Ошибка отправки напоминания: {e}")

        await asyncio.sleep(REMINDER_INTERVAL)

    logging.info(f"Завершение напоминаний для {chat_id}.")
    active_timers.pop(chat_id, None)  # Удаляем таймер из списка
    stop_spam_flags.pop(chat_id, None)  # Очищаем флаг


async def handle_stop_button(message: types.Message):
    """Остановка таймера"""
    chat_id = message.chat.id
    stop_spam_flags[chat_id] = True  # Останавливаем спам

    if chat_id in active_timers:
        try:
            # Пытаемся удалить задание, если оно еще существует
            active_timers[chat_id].remove()
        except JobLookupError:
            # Задание уже было удалено или выполнено
            logging.info(f"Таймер для {chat_id} уже был завершен")
        finally:
            # В любом случае очищаем запись
            active_timers.pop(chat_id, None)

    await message.answer(
        "⏹ Напоминания остановлены!", reply_markup=registered_kb)


async def handle_back_button(message: types.Message):
    """Возвращает пользователя в главное меню"""
    await message.answer(
        "Вы вернулись в главное меню.", reply_markup=registered_kb)


def setup_timer_handlers(dp):
    """Регистрация обработчиков таймера"""
    dp.message.register(handle_timer_button, F.text == '⏱ Запустить таймер')
    dp.message.register(handle_start_button, F.text == 'Старт')
    dp.message.register(process_meal_time, TimerStates.waiting_for_meal_time)
    dp.message.register(
        process_reminder_minutes, TimerStates.waiting_for_reminder_minutes)
    dp.message.register(handle_stop_button, F.text == 'Стоп')
    dp.message.register(handle_back_button, F.text == '⬅ Назад')
