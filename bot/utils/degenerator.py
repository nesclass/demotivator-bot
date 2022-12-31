# Предновогодний челлендж: прототип популярного «Ржакабота» (@super_rjaka_demotivator_bot)
# Минимальная жизнеспособная версия, нуждается в многочисленных доработках.

import os
import ffmpeg
import asyncio
import logging

# задний фон всех демотиваторов (чёрный квадрат с белым краем)
FFMPEG_BACKGROUND = ffmpeg.input("background.png")


# ключевая функция, враппер вокруг ffmpeg
async def generate_demotivator(input_file: str,
                               output_file: str,
                               text: str = "зачем"):
    v_in = ffmpeg.input(input_file)  # файл, из которого генерируется демик
    v_resized = v_in.video.filter(
        "scale",  # подгоняет исходник под окошко
        w=304, h=282  # магические числа ✨
    )

    v_overlap = ffmpeg.filter(
        (FFMPEG_BACKGROUND, v_resized),
        "overlay",  # накладывает исходник на окошко
        x=28, y=17,  # магические числа ✨,
    )

    # TODO: вторая строчка текста
    v_result = v_overlap.filter(
        "drawtext",  # рисует текст под демиком
        text=text,
        fontcolor="white",
        fontsize="27",  # TODO: перерасчёт размера шрифта в зависимости от длины текста
        x="(w-tw)/2",  # width - text width => по центру демика
        y="304+(371-304-th)/2",  # TODO: вынести параметры высоты нижней области в отдельную переменную
        font="Times New Roman"
    )

    v_output = v_result.output(output_file)  # экспорт демика в файл

    proc = await asyncio.create_subprocess_exec(
        os.getenv("FFMPEG_BIN") or "bins/ffmpeg",
        *v_output.compile()[1:],  # костыль?
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if stdout:
        logging.info(stdout.decode())
    if stderr:
        logging.error(stderr.decode())
