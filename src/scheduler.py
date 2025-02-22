
from aiogram import Bot
from tinydb import Query

from models import Remainder
from src.config import scheduler, timezone, db
from src.tasks import send_reminder

week_days = {
    "ПН": 0,
    "ВТ": 1,
    "СР": 2,
    "ЧТ": 3,
    "ПТ": 4,
    "СБ": 5,
    "ВС": 6,
}

def add_task(data: dict, bot: Bot) -> str:
    match data['type']:
        case 'dayly':
            job = add_daily_task(data, bot)
        case 'weekly':
            job = add_weekly_task(data, bot)
        case 'monthly':
            job = add_monthly_task(data, bot)
        case _:
            pass
    return job.id

def add_daily_task(data: dict, bot: Bot):
    return scheduler.add_job(
        send_reminder,
        'cron',
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,data)
    )

def add_weekly_task(data: dict, bot: Bot):
    return scheduler.add_job(
        send_reminder,
        'cron',
        day_of_week=week_days.get(data['week_day']),
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,data)
    )


def add_monthly_task(data: dict, bot: Bot):
    return scheduler.add_job(
        send_reminder,
        'cron',
        day=data['month_day'],
        hour=data['hour'],
        minute=data['minutes'],
        timezone=timezone,
        args=(bot,data)
    )

def add_tasks_from_db(bot: Bot):
    jobs = db.all()
    for job in jobs:
        old_task_id = job["task_id"]
        new_task_id = add_task(job, bot)
        Task = Query()
        db.update({'task_id': new_task_id}, Task.task_id == old_task_id)

def rm_all_tasks_from_db():
    for j in scheduler.get_jobs():
        j.remove()

def delete_task(task_id: str) -> None:
    for j in scheduler.get_jobs():
        data = j.args[1]
        if data["task_id"] == task_id:
            scheduler.remove_job(j.id)
            Task = Query()
            db.remove(Task.task_id == task_id)

def get_formatted_task(task_id: str) -> str | None:
    for j in scheduler.get_jobs():
        data = j.args[1]
        if data["task_id"] == task_id:
            return str(Remainder(**data))
    return None

def get_formatted_jobs() -> str:
    scheduled = []
    for j in scheduler.get_jobs():
        data = j.args[1]
        scheduled.append(str(Remainder(**data)))

    return "\n".join(scheduled)
