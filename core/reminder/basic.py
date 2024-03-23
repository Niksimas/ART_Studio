from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.database import database as db


scheduler = AsyncIOScheduler(timezone="Asia/Novosibirsk")


@scheduler.scheduled_job("cron", month=12, day=31)  # Новый год
@scheduler.scheduled_job("cron", month=3, day=8)  # 8 марта
@scheduler.scheduled_job("cron", month=6, day=1)  # День защиты детей
async def accrual_holiday_points():
    user_list = db.get_all_id_user()
    for i in user_list:
        actual_scope = db.get_scope_user(i)
        db.update_score_user(actual_scope + 10000, i)


@scheduler.scheduled_job("cron", hour=1, minute=0)  # ДР
async def accrual_birthdate_points():
    user_list = db.get_all_birthdate_user()
    for i in user_list:
        actual_scope = db.get_scope_user(i)
        db.update_score_user(actual_scope + 10000, i)
