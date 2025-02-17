import logging
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from keyboards import delete_task_keyboard, hour_keyboard, minutes_keyboard, type_keyboard, week_day_keyboard, month_day_keyboard, \
    confirm_keyboard
from commands import bot_commands
from config import API_TOKEN, remainder_types, db, timezone, scheduler
from scheduler import add_tasks_from_db, add_task, delete_task, get_formatted_jobs, rm_all_tasks_from_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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
    data["task_id"] = add_task(data, bot)
    db.insert(data)
    await message.answer("Уведомление добавлено", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@dp.message(Command("reminders"))
async def cmd_start(message: types.Message, state: FSMContext):
    for job in db.all():
        print(job)
    formated_reminders = get_formatted_jobs()
    await message.answer(f"текущие напоминания:\n\n{formated_reminders}")

@dp.message(Command("purge"))
async def cmd_start(message: types.Message, state: FSMContext):
    db.truncate()
    rm_all_tasks_from_db()
    await message.answer(f"Все напоминания удалены")
    
@dp.message(Command("delete"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(f"Какое напоминание удалить?", reply_markup=delete_task_keyboard(db.all()))
    
    
@dp.callback_query(lambda c: c.data.startswith("task_"))
async def handle_task_selection(callback: types.CallbackQuery):
    task_id = callback.data.split("_")[1]
    delete_task(task_id)
    await bot.send_message(callback.from_user.id, f"Напоминание {task_id} удалено")

async def main():
    add_tasks_from_db(bot)
    scheduler.start()
    await bot.set_my_commands(bot_commands)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())