import logging

from aiogram import Router, types, F
from aiogram.filters import Command
from database.create import SessionLocal

from database.models.user import User
from keyboards.keyboards import registered_kb, unregistered_kb

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    with SessionLocal() as session:
        user = session.query(User).filter(
            User.tg_id == message.from_user.id
        ).first()

        if user:
            await message.answer(
                f"С возвращением, {user.username or 'друг'}!",
                reply_markup=registered_kb
            )
        else:
            await message.answer(
                "Добро пожаловать! Выберите действие:",
                reply_markup=unregistered_kb
            )


@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def help_handler(message: types.Message) -> None:
    """
    Обработка команды /help с проверкой авторизации
    """
    try:
        with SessionLocal() as session:
            user = session.query(User).filter(
                User.tg_id == message.from_user.id
            ).first()

            help_text = (
                "❓ *Помощь по боту*\n\n"
                "Я помогу Вам отслеживать уровень сахара и Ваше питание!"
                " Вот что я умею:\n\n"
            )

            if user:
                # Текст для авторизованных пользователей
                help_text += (
                    "⏱ Запустить таймер - начать уровень сахара в крови\n"
                    "📊 Внести данные - добавить показатели сахара"
                    " или внести данные по еде\n"
                    "📈 Статистика - просмотреть ваши данные\n"
                    "ℹ️ О нас - информация о боте"
                )
                await message.answer(help_text, reply_markup=registered_kb)
            else:
                # Текст для неавторизованных пользователей
                help_text += (
                    "📝 Регистрация - создать аккаунт\n\n"
                    "Для начала работы зарегистрируйтесь!"
                )
                await message.answer(help_text, reply_markup=unregistered_kb)

    except Exception as e:
        logging.error(f"Ошибка в help_handler: {str(e)}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=unregistered_kb
        )
