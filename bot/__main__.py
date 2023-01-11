import os
from aiogram import executor

from bot import dp


if __name__ == "__main__":
    os.makedirs("inputs", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # TODO: init_handlers
    from bot.handlers import general  # noqa
    from bot.handlers import media  # noqa

    # TODO: init_middlewares
    from bot.utils.album import MediaMergeMiddleware
    dp.setup_middleware(MediaMergeMiddleware())

    executor.start_polling(dispatcher=dp, skip_updates=True)
