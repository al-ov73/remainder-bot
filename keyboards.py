import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.enums import ParseMode
from config import remainder_types

def confirm_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Да")
    builder.button(text="Нет")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def delete_task_keyboard(tasks):
    builder = InlineKeyboardBuilder()

    for t in tasks:
        builder.button(text=f"{t["type"]}{t["hour"]}:{t["minutes"]}", callback_data=f"task_{t['task_id']}")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def type_keyboard():
    builder = ReplyKeyboardBuilder()
    for value in remainder_types:
        builder.button(text=value)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)

def week_day_keyboard():
    builder = ReplyKeyboardBuilder()
    days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    for day in days:
        builder.button(text=day)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)

def hour_keyboard():
    builder = ReplyKeyboardBuilder()
    for hour in range(1, 25):
        builder.button(text=str(hour))
    builder.adjust(6)
    return builder.as_markup(resize_keyboard=True)

def month_day_keyboard():
    builder = ReplyKeyboardBuilder()
    for hour in range(1, 32):
        builder.button(text=str(hour))
    builder.adjust(6)
    return builder.as_markup(resize_keyboard=True)

def minutes_keyboard():
    builder = ReplyKeyboardBuilder()
    for minute in range(0, 60, 15):
        builder.button(text=str(minute))
    builder.adjust(4)
    return builder.as_markup(resize_keyboard=True)