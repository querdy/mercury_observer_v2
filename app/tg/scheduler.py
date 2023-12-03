from typing import Callable

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger


class SchedulerRepo:
    def __init__(self):
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        # self.scheduler.add_jobstore('mongodb', database=settings.DATABASE_NAME)
        self.scheduler.start()

    def get_user_jobs(self, user_id: int) -> list[Job]:
        return [job for job in self.scheduler.get_jobs() if job.name == str(user_id)]

    def create_job(self, function: Callable, params: dict, user_id: int,
                   every_minute: int, hour_start: int, hour_end: int,
                   minute_start: int, minute_end: int, days_of_week: list[int]) -> bool:
        try:
            self.scheduler.add_job(
                function,
                kwargs=params,
                trigger=CronTrigger(
                    hour=f"{hour_start}-{hour_end}" if hour_start < hour_end else f"{hour_start}-23, 0-{hour_end}",
                    minute=f"{minute_start}-{minute_end}/{every_minute}",
                    day_of_week=','.join(str(day) for day in days_of_week),
                ),
                name=str(user_id)
            )
            logger.info(f"{user_id} create job. func: {function.__name__}")
            return True
        except ValueError:
            logger.warning(f"{user_id} NOT create job. Params: {params}")
            return False

    def remove_user_jobs(self, user_id: int):
        [job.remove() for job in self.get_user_jobs(user_id=user_id)]
        logger.debug(f"all user {user_id} jobs removed")

    def remove_all_jobs(self):
        [job.remove() for job in self.scheduler.get_jobs()]
        logger.debug(f"all jobs removed")
