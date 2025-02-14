import logging
import asyncio


from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from keyboards import hour_keyboard, minutes_keyboard, type_keyboard, week_day_keyboard, month_day_keyboard, \
    confirm_keyboard
from commands import bot_commands
from config import API_TOKEN, remainder_types, db, timezone
from tasks import send_reminder


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

reminders = {}

class Remainder(StatesGroup):
    type = State()
    month_day = State()
    week_day = State()
    hour = State()
    minutes = State()
    confirm = State()
    text = State()

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
    await state.set_state(Remainder.minutes)

@dp.message(Remainder.minutes)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(minutes=message.text)
    await message.answer(f"Введите текст напоминания:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Remainder.text)

@dp.message(Remainder.text)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    await message.answer(
        f"Вы добавили напомиание:\n"
        f"Тип: {data['type']}\n"
        f"День месяца: {data['month_day']}\n"
        f"День недели: {data['week_day']}\n"
        f"Время: {data['hour']}:{data['minutes']}\n"
        f"Текст напоминания: {data['text']}",
        reply_markup=confirm_keyboard(),
    )
    await state.set_state(Remainder.confirm)

@dp.message(Remainder.confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    data["user_id"] = user_id
    print(data)
    db.insert(data)
    reminders[user_id] = data
    reminder_text = data['text']
    scheduler.add_job(
        send_reminder,
        'cron',
        day=data['month_day'], # day of month (1-31)
        day_of_week=['week_day'], # number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone, # timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)
        args=(bot,user_id,reminder_text)
    )
    scheduler.start()
    await message.answer("Уведомление добавлено", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@dp.message(Command("reminders"))
async def cmd_start(message: types.Message, state: FSMContext):
    scheduler.print_jobs()
    reminders = [f"{r}" for r in db.all()]
    formated_reminders = "\n\n".join(reminders)
    await message.answer(f"текущие напоминания:\n\n{formated_reminders}")

def add_tasks_from_db():
    jobs = db.all()
    for job in jobs:
        scheduler.add_job(
            send_reminder,
            'cron',
            hour=job['hour'],
            minute=job['minutes'],
            timezone=timezone,
            args=(bot,job['user_id'],job['text'])
        )

async def main():
    add_tasks_from_db()
    await bot.set_my_commands(bot_commands)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())