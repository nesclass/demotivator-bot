# Предновогодний челлендж: прототип популярного «Ржакабота» (@super_rjaka_demotivator_bot)
# Минимальная жизнеспособная версия, нуждается в многочисленных доработках.

import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# TODO: система конфигурации (pydantic + .json)

bot = Bot(os.getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
