from enum import Enum

from aiogram.types import BotCommand
from dataclasses import dataclass


@dataclass
class TelegramCommand:
    name: str
    title: str

    @property
    def command(self) -> str:
        return f"/{self.name}"


class TelegramCommands(Enum):
    START = TelegramCommand("start", "Старт")
    REMINDERS = TelegramCommand("reminders", "Напоминания")
    DELETE = TelegramCommand("delete", "Удалить напоминание")
    PURGE = TelegramCommand("purge", "Удалить все")


bot_commands = [BotCommand(command=c.value.command, description=c.value.title) for c in TelegramCommands]
