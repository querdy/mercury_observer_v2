from typing import Callable

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from app.settings import settings


class SchedulerRepo:
    def __init__(self):
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        # self.scheduler.add_jobstore('mongodb', database=settings.DATABASE_NAME)
        self.scheduler.start()

    def get_user_jobs(self, user_id: int, service_name: str) -> list[Job]:
        return [job for job in self.scheduler.get_jobs() if job.name == f"{user_id}_{service_name}"]

    def get_all_user_jobs(self, user_id: int) -> list[Job]:
        return [job for job in self.scheduler.get_jobs() if str(user_id) in job.name]

    def create_job(self, function: Callable, params: dict, user_id: int, service_name: str,
                   every_minute: int, hour_start: int, hour_end: int,
                   minute_start: int, minute_end: int, days_of_week: list[int]) -> bool:
        if minute_end == 0:
            minute_end -= 1
        if minute_start == 0:
            minute_start += 3
        try:
            self.scheduler.add_job(
                function,
                kwargs=params,
                trigger=CronTrigger(
                    hour=f"{hour_start}-{hour_end}" if hour_start < hour_end else f"{hour_start}-23, 0-{hour_end}",
                    minute=f"{minute_start}-{minute_end}/{every_minute}" if minute_start < minute_end else f"*/{every_minute}",
                    day_of_week=','.join(str(day) for day in days_of_week),
                ),
                name=f"{user_id}_{service_name}"
            )
            logger.info(f"{user_id} create job. name: {user_id}_{service_name}")
            return True
        except ValueError as err:
            logger.warning(f"{user_id} NOT create job. Err: {err}, Params: {params}")
            return False

    def remove_user_jobs(self, user_id: int, service_name: str):
        [job.remove() for job in self.get_user_jobs(user_id=user_id, service_name=service_name)]
        logger.debug(f"all user {user_id} jobs removed")

    def remove_all_jobs(self):
        [job.remove() for job in self.scheduler.get_jobs()]
        logger.debug(f"all jobs removed")
