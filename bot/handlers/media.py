import asyncio
import logging
import functools

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import bot, dp
from bot.utils.degenerator import generate_demotivator
from bot.keyboards.media import provide_text_keyboard

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# fsm, состояние формы при создании демика
class CreateDemotivator(StatesGroup):
    provide_text = State()


# функция враппер, отправляет результат картинкой
async def send_photo(message: types.Message, output: str):
    file = types.InputFile(output, "result.jpg")
    await message.reply_photo(file)


# функция враппер, отправляет результат гифкой (анимацией)
async def send_animation(message: types.Message, output: str):
    file = types.InputFile(output, "result.mp4")
    await message.reply_animation(file)  # animation <-> gif


# формат -> функция враппер
content_type_handlers = {
    "mp4": send_animation,
    "jpg": send_photo
}


# обработчик медиа вложений
async def process_media(
        message: types.Message,             # основное сообщение пользователя (медиа-контент и/или текст)
        state: FSMContext,                  # контекст состояния, необходим для его управлением
        file_id: str,                       # идентификатор медиа-вложения
        file_format: str,                   # формат медиа-вложения (mp4, jpg)
        # TODO: подумать над целесообразностью этого параметра, вероятно его можно убрать
        is_album: bool,                     # отправлялись ли вложения как альбом
        text: str,                          # текст для демика (случайный, пользовательский)
        menu: types.Message | None = None,  # оригинал контекстного меню с клавиатурой (если было вызвано)
):
    file = await bot.get_file(file_id)
    if file.file_size > MAX_FILE_SIZE:
        await message.reply("Файл не должен превышать 20 МБ.")
        return

    # если текст не был предоставлен (скинули исключительно медиа-контент)
    if not text:
        await CreateDemotivator.provide_text.set()  # включить состояние "зачатия демика"

        menu = await message.reply("Вы не прикрепили комментарий для демика.\n"
                                   "Введите комментарий или воспользуйтесь контекстным меню:",
                                   reply_markup=provide_text_keyboard())

        # сохранить мета-данные состояния
        return await state.update_data(
            file_id=file_id,
            file_format=file_format,
            is_album=is_album,
            menu=menu
        )

    # отказ от сверх медиа перегрузок с помощью ALBUM MERGE
    reply = "Ожидайте, обработка займёт до 5 секунд..."
    if is_album:
        reply += "\n\nОбратите внимание, что бот обработает " \
                 "исключительно первое вложение из медиа-группы."

    if menu:  # если есть контекстное меню
        await menu.edit_text(text=reply)
    else:  # если нету контекстного меню
        await message.reply(reply)

    # TODO: удаление темп-файлов
    input_file = f"inputs/{message.message_id}.{file_format}"  # темп-файл для исходника
    output_file = f"results/{message.message_id}.{file_format}"  # темп-файл для демика

    await bot.download_file(file.file_path, input_file)

    """
    try:
        # генерация демика
        await generate_demotivator(input_file, output_file, text)
    except ffmpeg.Error as exc:
        logging.exception(exc)
        return await message.reply("Обработка демика была прервана ошибкой FFmpeg.")
    """

    try:
        # TODO: ну хуйня же, не? может стоит переделать..
        p_func = functools.partial(generate_demotivator, input_file, output_file, text)
        await asyncio.get_running_loop().run_in_executor(None, p_func)
    except Exception as exc:
        logging.exception(exc)
        return await message.reply("Обработка демика была прервана ошибкой.")

    # вызов функции враппера
    await content_type_handlers[file_format](message, output_file)


# отменить процесс создания демика (вызвано контекстное меню)
@dp.callback_query_handler(state=CreateDemotivator.provide_text, text="cancel")
async def cancel_process(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    return await query.message.edit_text(text="Вы отменили создание демика.")


# использовать случайный текст в демике (вызвано контекстное меню)
@dp.callback_query_handler(state=CreateDemotivator.provide_text, text="random-text")
async def process_random_text(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await state.finish()

        # немного костыльный подход, стоит пересмотреть
        # вытягивание всей информации из состояния прямо в хендлере

        await process_media(
            query.message.reply_to_message, state,
            data["file_id"],
            data["file_format"],
            data["is_album"],
            "зачем",  # TODO: случайные слова,
            data["menu"]
        )


# использовать пользовательский текст в демике (вызвано контекстное меню)
@dp.message_handler(state=CreateDemotivator.provide_text)
async def process_text(message: types.Message, state: FSMContext):
    if not message.text:
        return await message.reply("Пожалуйста, укажите комментарий для демика.")
    elif len(message.text) > 32:
        return await message.reply("Комментарий должен быть меньше 32 символов.")

    async with state.proxy() as data:
        await state.finish()

        # немного костыльный подход, стоит пересмотреть
        # вытягивание всей информации из состояния прямо в хендлере

        await process_media(
            message, state,
            data["file_id"],
            data["file_format"],
            data["is_album"],
            message.text,
            data["menu"]
        )


# хендлер для фотографий
@dp.message_handler(content_types=types.ContentType.PHOTO)
@dp.throttled(rate=2)  # троттлинг для надёжности
async def process_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id  # highest quality photo (последний элемент в массиве)
    await process_media(
        message, state,
        file_id, "jpg",
        message.media_group_id,  # может быть равна None
        message.caption  # при отправке медиа-контента message.text становится message.caption
    )


# хендлер для видео и гифок (анимаций)
@dp.message_handler(content_types=[types.ContentType.VIDEO,
                                   types.ContentType.ANIMATION])
@dp.throttled(rate=2)  # троттлинг для надёжности
async def process_video(message: types.Message, state: FSMContext):
    file_id = message[message.content_type].file_id
    await process_media(
        message, state,
        file_id, "mp4",
        message.media_group_id,  # может быть равна None
        message.caption  # при отправке медиа-контента message.text становится message.caption
    )
