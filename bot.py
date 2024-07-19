import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from config import API_TOKEN
from handlers.auth_handlers import register_auth_handlers
# from handlers.admin_handlers import register_admin_handlers
from handlers.student_handlers import register_student_handlers
from database import init_db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

register_auth_handlers(dp)
# register_admin_handlers(dp)
register_student_handlers(dp)

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
