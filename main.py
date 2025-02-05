import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

import asyncio
import os
from dotenv import load_dotenv
from keyboards import hour_keyboard, minutes_keyboard, type_keyboard, week_day_keyboard, month_day_keyboard
from config import remainder_types

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Определение состояний (FSM)
class Remainder(StatesGroup):
    type = State()
    month_day = State()
    week_day = State()
    hour = State()
    minutes = State()
    confirm = State()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Введи тип напоминания:", reply_markup=type_keyboard())
    await state.set_state(Remainder.type)

# Обработка типа
@dp.message(Remainder.type)
async def process_name(message: types.Message, state: FSMContext):
    remainder_type = remainder_types[message.text]
    await state.update_data(type=remainder_type)
    match remainder_type:
        case "dayly":
            await state.update_data(month_day="")
            await state.update_data(week_day="")
            await message.answer(f"Введите часы:", reply_markup=hour_keyboard())
            await state.set_state(Remainder.hour)
        case "weekly":
            await state.update_data(month_day="")
            await message.answer(f"В какой день недели делать напоминание?", reply_markup=week_day_keyboard())
            await state.set_state(Remainder.week_day)
        case "monthly":
            await state.update_data(week_day="")
            await message.answer(f"Какого числа делать напоминание?", reply_markup=month_day_keyboard())
            await state.set_state(Remainder.month_day)
        case _:
            pass

@dp.message(Remainder.week_day)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(week_day=message.text)
    await message.answer(f"Введите часы:", reply_markup=hour_keyboard())
    await state.set_state(Remainder.hour)

@dp.message(Remainder.month_day)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(month_day=message.text)
    await message.answer(f"Введите часы:", reply_markup=hour_keyboard())
    await state.set_state(Remainder.hour)
    
@dp.message(Remainder.hour)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(hour=message.text)
    await message.answer(f"Введите минуты:", reply_markup=minutes_keyboard())
    await state.set_state(Remainder.confirm)

# # Обработка подтверждения
@dp.message(Remainder.confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    await state.update_data(minutes=message.text)
    data = await state.get_data()
    await message.answer(
        f"Добавлено напоминание:\n"
        f"Тип: {data['type']}\n"
        f"День месяца: {data['month_day']}\n"
        f"День недели: {data['week_day']}\n"
        f"Время: {data['hour']}:{data["minutes"]}\n",
        reply_markup=ReplyKeyboardRemove(),
    )
    print('стейт: ', data)
    await state.clear()



# # Обработка возраста
# @dp.message(Remainder.age)
# async def process_age(message: types.Message, state: FSMContext):
#     if not message.text.isdigit():
#         await message.answer("Пожалуйста, введи число.")
#         return

#     await state.update_data(age=int(message.text))
#     await message.answer("Теперь укажи свой пол:", reply_markup=gender_keyboard())
#     await state.set_state(Remainder.gender)


# # Обработка пола
# @dp.message(Remainder.gender)
# async def process_gender(message: types.Message, state: FSMContext):
#     if message.text not in ["Мужской", "Женский"]:
#         await message.answer("Пожалуйста, выбери пол из предложенных вариантов.")
#         return

#     await state.update_data(gender=message.text)
#     data = await state.get_data()
#     await message.answer(
#         f"Проверь свои данные:\n"
#         f"Имя: {data['name']}\n"
#         f"Возраст: {data['age']}\n"
#         f"Пол: {data['gender']}\n\n"
#         f"Всё верно?",
#         reply_markup=confirm_keyboard(),
#     )
#     await state.set_state(Remainder.confirm)





async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
