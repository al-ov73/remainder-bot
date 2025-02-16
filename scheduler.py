from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import API_TOKEN, remainder_types, db, timezone


scheduler = AsyncIOScheduler()

week_days = {
    "ПН": 0,
    "ВТ": 1,
    "СР": 2,
    "ЧТ": 3,
    "ПТ": 4,
    "СБ": 5,
    "ВС": 6,
}

def add_task(data: dict) -> None:
    match data['type']:
        case 'dayly':
            add_daily_task(data)
        case 'weekly':
            add_weekly_task(data)
        case 'monthly':
            add_monthly_task(data)
        case _:
            pass

def add_daily_task(data: dict):
    scheduler.add_job(
        send_reminder,
        'cron',
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,user_id,reminder_text)
    )
    scheduler.start()

def add_weekly_task(data: dict):
    scheduler.add_job(
        send_reminder,
        'cron',
        day_of_week=week_days.get(data['week_day']),
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,user_id,reminder_text)
    )
    scheduler.start()

def add_monthly_task(data: dict):
    scheduler.add_job(
        send_reminder,
        'cron',
        day=data['month_day'],
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,user_id,reminder_text)
    )
    scheduler.start()

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