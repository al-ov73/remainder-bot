from config import API_TOKEN, remainder_types, db, timezone, scheduler
from aiogram import Bot

from tasks import send_reminder

week_days = {
    "ПН": 0,
    "ВТ": 1,
    "СР": 2,
    "ЧТ": 3,
    "ПТ": 4,
    "СБ": 5,
    "ВС": 6,
}

def add_task(data: dict, bot: Bot) -> None:
    match data['type']:
        case 'dayly':
            add_daily_task(data, bot)
        case 'weekly':
            add_weekly_task(data, bot)
        case 'monthly':
            add_monthly_task(data, bot)
        case _:
            pass

def add_daily_task(data: dict, bot: Bot):
    scheduler.add_job(
        send_reminder,
        'cron',
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,data["user_id"],data['text'])
    )

def add_weekly_task(data: dict, bot: Bot):
    scheduler.add_job(
        send_reminder,
        'cron',
        day_of_week=week_days.get(data['week_day']),
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,data["user_id"],data['text'])
    )


def add_monthly_task(data: dict, bot: Bot):
    scheduler.add_job(
        send_reminder,
        'cron',
        day=data['month_day'],
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,data["user_id"],data['text'])
    )

def add_tasks_from_db(bot: Bot):
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