# Предновогодний челлендж: прототип популярного «Ржакабота» (@super_rjaka_demotivator_bot)
# Минимальная жизнеспособная версия, нуждается в многочисленных доработках.

import ffmpeg

# задний фон всех демотиваторов (чёрный квадрат с белым краем)
FFMPEG_BACKGROUND = ffmpeg.input("background.png")


# TODO: async via ffmpeg.compile + asyncio.subprocess
# ключевая функция, враппер вокруг ffmpeg
def generate_demotivator(input_file: str,
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
    v_output.run(cmd=f"bins/ffmpeg")  # TODO: ffmpeg location in env
