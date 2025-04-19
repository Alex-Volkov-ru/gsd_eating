from aiogram import Router, types, F

router = Router()

@router.message(F.text == '🍎 Статистика по еде')
async def show_food_stats(message: types.Message):
    """Статистика по питанию"""
    await message.answer("Статистика по питанию...")