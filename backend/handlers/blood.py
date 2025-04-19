import logging
import calendar

from datetime import datetime
from decimal import Decimal
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.orm import Session

from database.create import get_db
from database.models.user import User
from database.models.blood_type import BloodType
from database.models.blood import BloodRecord
from keyboards.keyboards import registered_kb, get_data_kb

logger = logging.getLogger(__name__)

class BloodSugarStates(StatesGroup):
    waiting_for_level = State()
    waiting_for_type = State()
    waiting_for_date = State()

router = Router()

def get_days_keyboard():
    today = datetime.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days = [str(day) for day in range(1, days_in_month + 1)]

    buttons = []
    row = []
    for day in days:
        row.append(InlineKeyboardButton(text=day, callback_data=f"blood_day_{day}"))
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="blood_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_blood_types_keyboard():
    db: Session = next(get_db())
    buttons = [
        [InlineKeyboardButton(text=t.name, callback_data=f"blood_type_{t.id}")]
        for t in db.query(BloodType).all()
    ]
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="blood_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(F.text == '🩸 Внести показатели сахара в крови')
async def start_add_blood_sugar(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите уровень сахара в крови (ммоль/л):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(BloodSugarStates.waiting_for_level)

@router.message(BloodSugarStates.waiting_for_level)
async def process_blood_level(message: types.Message, state: FSMContext):
    try:
        level = float(Decimal(message.text.replace(',', '.')))
        if not (0 < level <= 30):
            raise ValueError()
        
        await state.update_data(glucose=level)
        await message.answer(
            "Выберите тип измерения:",
            reply_markup=get_blood_types_keyboard()
        )
        await state.set_state(BloodSugarStates.waiting_for_type)
    except:
        await message.answer(
            "❌ Введите корректный уровень (например: 5.2)",
            reply_markup=get_data_kb()
        )

@router.callback_query(BloodSugarStates.waiting_for_type, F.data.startswith('blood_type_'))
async def process_blood_type(callback: CallbackQuery, state: FSMContext):
    try:
        type_id = int(callback.data.split('_')[2])
        db: Session = next(get_db())
        blood_type = db.query(BloodType).get(type_id)
        
        await state.update_data(
            blood_type_id=blood_type.id,
            blood_type_name=blood_type.name
        )
        await callback.message.answer(
            f"Вы выбрали: {blood_type.name}\n"
            "Выберите день месяца:",
            reply_markup=get_days_keyboard()
        )
        await callback.message.delete()
        await state.set_state(BloodSugarStates.waiting_for_date)
    except:
        await callback.message.answer(
            "❌ Ошибка выбора типа",
            reply_markup=get_data_kb()
        )

@router.callback_query(BloodSugarStates.waiting_for_date, F.data.startswith('blood_day_'))
async def process_blood_day(callback: CallbackQuery, state: FSMContext):
    try:
        day = int(callback.data.split('_')[2])
        data = await state.get_data()
        record_date = datetime.today().replace(day=day)
        
        db: Session = next(get_db())
        user = db.query(User).filter(User.tg_id == callback.from_user.id).first()
        
        db.add(BloodRecord(
            user_id=user.id,
            blood_type_id=data['blood_type_id'],
            glucose=data['glucose'],
            date_time=record_date
        ))
        db.commit()
        
        await callback.message.answer(
            f"✅ Данные сохранены!\n\n"
            f"Уровень: {data['glucose']} ммоль/л\n"
            f"Тип: {data['blood_type_name']}\n"
            f"Дата: {record_date.strftime('%d.%m.%Y')}",
            reply_markup=registered_kb
        )
        await callback.message.delete()
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")
        await callback.message.answer(
            "❌ Ошибка сохранения данных",
            reply_markup=registered_kb
        )

@router.message(BloodSugarStates.waiting_for_date)
async def process_blood_date_manual(message: types.Message, state: FSMContext):
    try:
        record_date = datetime.strptime(message.text, "%d.%m.%Y")
        if record_date.month != datetime.today().month:
            raise ValueError()
        
        data = await state.get_data()
        db: Session = next(get_db())
        user = db.query(User).filter(User.tg_id == message.from_user.id).first()
        
        db.add(BloodRecord(
            user_id=user.id,
            blood_type_id=data['blood_type_id'],
            glucose=data['glucose'],
            date_time=record_date
        ))
        db.commit()
        
        await message.answer(
            f"✅ Данные сохранены!\n\n"
            f"Уровень: {data['glucose']} ммоль/л\n"
            f"Тип: {data['blood_type_name']}\n"
            f"Дата: {record_date.strftime('%d.%m.%Y')}",
            reply_markup=registered_kb
        )
        await state.clear()
    except:
        await message.answer(
            "❌ Введите дату в формате ДД.ММ.ГГГГ (текущий месяц)",
            reply_markup=registered_kb
        )

@router.callback_query(F.data == "blood_cancel")
async def cancel_blood_input(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Ввод данных отменен",
        reply_markup=registered_kb
    )
    await callback.message.delete()