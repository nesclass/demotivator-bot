# Предновогодний челлендж: прототип популярного «Ржакабота» (@super_rjaka_demotivator_bot)
# Минимальная жизнеспособная версия, нуждается в многочисленных доработках

import os
import uuid
import ffmpeg

from aiogram import Bot, Dispatcher, executor, types

FFMPEG_BACKGROUND = ffmpeg.input("background.png")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

bot = Bot(token=os.getenv("BOT_TOKEN"),  # TODO: система конфигурации (pydantic + .json)
          parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler()
async def general(message: types.Message):
    return await message.reply("В данный момент поддерживаются только видео и гифки.\n"
                               "Текстовый ввод временный недоступен, максимальный вес файла: 20Мб.")


@dp.message_handler(content_types=[types.ContentType.VIDEO,
                                   types.ContentType.ANIMATION])
async def process_video(message: types.Message):
    file_id = message.video.file_id if message.video \
        else message.animation.file_id

    file = await bot.get_file(file_id)
    if file.file_size > MAX_FILE_SIZE:
        return await message.reply("Файл не должен превышать 20 Мб.")

    await message.reply("Ожидайте, обработка гифки займёт до 5 секунд...")

    task_id = uuid.uuid4()
    await bot.download_file(file.file_path, f"inputs/{task_id}.mp4")

    v_in = ffmpeg.input(f"inputs/{task_id}.mp4")
    v_resized = v_in.video.filter("scale", w=304, h=282)  # магические числа ✨

    v_overlap = ffmpeg.filter(
        (FFMPEG_BACKGROUND, v_resized),
        "overlay",
        x=28, y=17,  # магические числа ✨
        format="yuv420"
    )

    # TODO: вторая строчка текста
    v_result = v_overlap.filter(
        "drawtext",
        text="зачем",  # TODO: ввод текста пользователем
        fontcolor="white",
        fontsize="27",  # TODO: перерасчёт размера шрифта в зависимости от длины текста
        x="(w-tw)/2",
        y="304+(371-304-th)/2",  # магические числа ✨
        font="Times New Roman"
    )

    v_result.output(f"results/{task_id}.mp4") \
        .run(cmd="bins/ffmpeg.exe")  # TODO: async via ffmpeg.compile + asyncio.subprocess

    file = types.InputFile(f"results/{task_id}.mp4", "result.mp4")
    await message.answer_animation(file)  # TODO: удаление файлов после работы


if __name__ == "__main__":
    os.makedirs("inputs", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # TODO: graceful shutdown
    executor.start_polling(dispatcher=dp, skip_updates=True)
