import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from app.middlewares.databases import DatabaseMiddleware
from app.middlewares.scheduler import SchedulerMiddleware
from app.middlewares.user import UserMiddleware
from app.settings import settings
from app.tg.router import base_router
from app.tg.scheduler import SchedulerRepo


async def main():
    bot = Bot(token=settings.API_TOKEN, parse_mode=ParseMode.HTML)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.update.middleware(SchedulerMiddleware(scheduler=SchedulerRepo()))
    dispatcher.update.middleware(DatabaseMiddleware(url=str(settings.DB_DSN)))
    dispatcher.update.middleware(UserMiddleware())
    dispatcher.include_router(base_router)
    dispatcher.startup.register(startup)
    await dispatcher.start_polling(bot)


async def startup():
    logger.info('Bot is running!')

if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stdout, level='DEBUG')
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
