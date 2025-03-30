from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from datetime import datetime

from database.create import SessionLocal
from database.models.user import User
from keyboards.keyboards import registered_kb

router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_name = State()


@router.message(Command("register"))
@router.message(F.text == "📝 Регистрация")
async def start_register(message: Message, state: FSMContext):
    with SessionLocal() as session:
        existing_user = session.query(User).filter(
            User.tg_id == message.from_user.id
        ).first()

        if existing_user:
            await message.answer(
                "Вы уже зарегистрированы!",
                reply_markup=registered_kb
            )
            return

    await message.answer(
        "Как к вам обращаться? (Введите ваше имя):",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationStates.waiting_for_name)


@router.message(RegistrationStates.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext):
    user_name = message.text.strip()

    if len(user_name) < 2:
        await message.answer("Имя слишком короткое. Введите еще раз:")
        return

    with SessionLocal() as session:
        new_user = User(
            tg_id=message.from_user.id,
            username=user_name,
            register_date=datetime.now()
        )
        session.add(new_user)
        session.commit()

    await message.answer(
        f"✅ Регистрация завершена!\nПриятно познакомиться, {user_name}!",
        reply_markup=registered_kb
    )
    await state.clear()
