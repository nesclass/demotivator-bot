import os
import cv2
import numpy as np

from PIL import ImageFont, ImageDraw, Image

FRAME_MARGIN_X = 24  # отступ до окантовки фрейма по Ox
FRAME_MARGIN_Y = 15  # отступ до окантовки фрейма по Oy
FRAME_THICKNESS = 1  # размер окантовки
FRAME_INNER_PADDING = 3  # внутренний отступ до медиа (без учёта толщины)

MEDIA_WIDTH = 306  # длина медиа в фрейме
MEDIA_HEIGHT = 284  # ширина медиа в фрейме

TEXT_AREA_HEIGHT = 68  # высота области для текста
TEXT_DEFAULT_FONT_SIZE = 28  # дефолтный размер шрифта
TEXT_CONTAINER_PADDING = 14  # отступы контейнера

# margin - padding - media - padding - margin
WIDTH = 2 * FRAME_MARGIN_X + 2 * FRAME_INNER_PADDING + MEDIA_WIDTH
# margin - padding - media - padding - text
HEIGHT = FRAME_MARGIN_Y + 2 * FRAME_INNER_PADDING + MEDIA_HEIGHT + TEXT_AREA_HEIGHT

# margin - padding - media - padding - text
MEDIA_TOP = FRAME_MARGIN_Y + FRAME_INNER_PADDING
MEDIA_BOTTOM = HEIGHT - TEXT_AREA_HEIGHT - FRAME_INNER_PADDING

# margin - padding - media - padding - margin
MEDIA_LEFT = FRAME_MARGIN_X + FRAME_INNER_PADDING
MEDIA_RIGHT = WIDTH - FRAME_MARGIN_X - FRAME_INNER_PADDING

# margin - padding - container[text] - padding - margin
MAX_TEXT_LENGTH = WIDTH - 2 * FRAME_MARGIN_X - 2 * TEXT_CONTAINER_PADDING

TEMPLATE = cv2.rectangle(
    # чёрный фон по размерам медиа
    img=np.zeros(
        (HEIGHT, WIDTH, 3),
        dtype=np.uint8
    ),

    # верхний левый угол окантовки
    pt1=(FRAME_MARGIN_X,
         FRAME_MARGIN_Y),

    # нижний правый угол окантовки
    pt2=(WIDTH - FRAME_MARGIN_X,
         HEIGHT - TEXT_AREA_HEIGHT),

    color=(255, 255, 255),
    thickness=FRAME_THICKNESS
)

# кэш для сгенерированных размеров шрифтов
# TODO: пре-генерация? возможно целесообразнее
cached_sizes: dict[int, ImageFont] = {}


# достать шрифт из кэша, либо сгенерировать новый
def get_font_by_size(size: int) -> ImageFont:
    if size in cached_sizes:
        return cached_sizes[size]

    font = ImageFont.truetype(os.getenv("FONT_PATH", "font.ttf"), size)
    cached_sizes[size] = font

    return font


# подобрать шрифт по (размеру) текста
def generate_font_from_text(text: str) -> ImageFont:
    font = get_font_by_size(TEXT_DEFAULT_FONT_SIZE)
    text_length = font.getlength(text)

    # если текст больше дозволенного
    if text_length > MAX_TEXT_LENGTH:
        # изменение размера шрифта пропорционально превышению
        ratio = MAX_TEXT_LENGTH / text_length
        font_size = int(TEXT_DEFAULT_FONT_SIZE * ratio)
        font_size += font_size % 2  # 23 -> 24, 25 -> 26
        font = get_font_by_size(int(font_size))

    return font


# манипуляция с масштабированием и наложением фрейма
def modify_template_by_frame(template: np.ndarray, frame: np.ndarray):
    frame = cv2.resize(
        frame,
        (MEDIA_WIDTH, MEDIA_HEIGHT),
        # interpolation=cv2.INTER_AREA
    )

    # замена пикселей в области y:x на фрейм
    template[MEDIA_TOP:MEDIA_BOTTOM, MEDIA_LEFT:MEDIA_RIGHT] = frame


# запись видео демика
def write_video(input_file: str, output_file: str, template: np.ndarray):
    stream = cv2.VideoCapture(input_file)

    out = cv2.VideoWriter(
        output_file,
        cv2.VideoWriter_fourcc(*'mp4v'),
        stream.get(cv2.CAP_PROP_FPS),
        (WIDTH, HEIGHT)
    )

    while stream.isOpened():
        flag, frame = stream.read()
        if not flag:
            break

        modify_template_by_frame(template, frame)
        out.write(template)

    stream.release()
    out.release()


# запись фото демика
def write_image(input_file: str, output_file: str, template: np.ndarray):
    image = cv2.imread(input_file)
    modify_template_by_frame(template, image)
    cv2.imwrite(output_file, template)


def generate_demotivator(input_file: str, output_file: str, text: str = "зачем"):
    # opencv image (numpy matrix) -> pil image
    im_template = Image.fromarray(TEMPLATE)
    im_draw = ImageDraw.Draw(im_template)
    font = generate_font_from_text(text)

    im_draw.text(
        # TODO: манипуляции с матрицами, аккуратное выравнивание по центру
        xy=(WIDTH / 2, HEIGHT - TEXT_AREA_HEIGHT / 2),
        text=text,
        font=font,
        fill="#ffffff",
        anchor="mm"
    )

    # pil image -> opencv image (numpy matrix)
    template = np.array(im_template)  # noqa

    if input_file.endswith(".mp4"):  # если видео
        return write_video(input_file, output_file, template)
    elif input_file.endswith(".jpg"):  # если изображение
        return write_image(input_file, output_file, template)

    # что это за херня?
    raise NotImplementedError
