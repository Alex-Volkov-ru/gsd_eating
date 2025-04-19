from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import registered_kb, get_data_kb

router = Router()

@router.message(F.text == '📊 Внести данные')
async def handle_data_menu(message: types.Message):
    """Главное меню внесения данных"""
    await message.answer(
        "Выберите тип данных для внесения:",
        reply_markup=get_data_kb()
    )

@router.message(F.text == '⬅ Назад')
async def handle_back_from_data(message: types.Message):
    """Возврат в главное меню"""
    await message.answer(
        "Возвращаемся в главное меню",
        reply_markup=registered_kb
    )