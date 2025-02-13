import logging

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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
from tasks import send_reminder

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для хранения напоминаний
reminders = {}

class Remainder(StatesGroup):
    type = State()
    month_day = State()
    week_day = State()
    hour = State()
    minutes = State()
    confirm = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Введи тип напоминания:", reply_markup=type_keyboard())
    await state.set_state(Remainder.type)

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

@dp.message(Remainder.confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    await state.update_data(minutes=message.text)
    data = await state.get_data()
    await message.answer(
        f"Добавлено напоминание:\n"
        f"Тип: {data['type']}\n"
        f"День месяца: {data['month_day']}\n"
        f"День недели: {data['week_day']}\n"
        f"Время: {data['hour']}:{data['minutes']}\n",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    user_id = message.from_user.id
    reminders[user_id] = data
    # hour=int(data['hour'])
    # minute=int(data['minutes'])
    text = "Напоминание!!!"
    timezone = pytz.timezone("Etc/GMT-4")
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_reminder,
        'cron',
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,user_id,text)
    )
    scheduler.start()

    await state.clear()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())