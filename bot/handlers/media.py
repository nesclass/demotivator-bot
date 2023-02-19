import time
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


class CreateDemotivator(StatesGroup):
    provide_text = State()


async def send_photo(message: types.Message, output: str):
    """Sends result as a photo"""
    file = types.InputFile(output, "result.jpg")
    await message.reply_photo(file)


async def send_animation(message: types.Message, output: str):
    """Sends result as an animation (gif)"""
    file = types.InputFile(output, "result.mp4")
    await message.reply_animation(file)  # animation <-> gif


content_type_handlers = {
    "mp4": send_animation,
    "jpg": send_photo
}


async def process_media(
        message: types.Message,
        state: FSMContext,
        file_id: str,
        file_format: str,

        # TODO: rethink if this is actually needed, remove if not
        is_album: bool,

        text: str,
        menu: types.Message | None = None,
):
    """
    Media-attachments handler
    :param message: main user message (media-content and/or text)
    :param state: FSM state context, used for state management
    :param file_id:
    :param file_format: mp4, jpg
    :param is_album:
    :param text: text for demotivator
    :param menu: original context menu with keyboard (if present)
    :return:
    """
    file = await bot.get_file(file_id)
    if file.file_size > MAX_FILE_SIZE:
        await message.reply("Файл не должен превышать 20 МБ.")
        return

    # No text present (media-attachment only)
    if not text:
        await CreateDemotivator.provide_text.set()

        menu = await message.reply("Вы не прикрепили комментарий для демика.\n"
                                   "Введите комментарий или воспользуйтесь контекстным меню:",
                                   reply_markup=provide_text_keyboard())

        return await state.update_data(
            file_id=file_id,
            file_format=file_format,
            is_album=is_album,
            menu=menu
        )

    # Use only first attachment from album, to avoid overloading
    reply = "Ожидайте, обработка займёт до 5 секунд..."
    if is_album:
        reply += "\n\nОбратите внимание, что бот обработает " \
                 "исключительно первое вложение из медиа-группы."

    if menu:
        await menu.edit_text(text=reply)
    else:
        await message.reply(reply)

    # TODO: remove temporary files
    input_file = f"inputs/{message.message_id}.{file_format}"  # temporary file for input
    output_file = f"results/{message.message_id}.{file_format}"  # temporary file for output

    await bot.download_file(file.file_path, input_file)

    try:
        # TODO: refactor
        p_func = functools.partial(generate_demotivator, input_file, output_file, text)
        await asyncio.get_running_loop().run_in_executor(None, p_func)
    except Exception as exc:
        logging.exception(exc)
        return await message.reply("Обработка демика была прервана ошибкой.")

    # call wrapper function
    await content_type_handlers[file_format](message, output_file)


@dp.callback_query_handler(state=CreateDemotivator.provide_text, text="cancel")
async def cancel_process(query: types.CallbackQuery, state: FSMContext):
    """Cancel process of creating demotivator"""
    await state.finish()
    return await query.message.edit_text(text="Вы отменили создание демика.")


@dp.callback_query_handler(state=CreateDemotivator.provide_text, text="random-text")
async def process_random_text(query: types.CallbackQuery, state: FSMContext):
    """Use random text in demotivator"""
    async with state.proxy() as data:
        await state.finish()

        # noqa, refactor

        await process_media(
            query.message.reply_to_message, state,
            data["file_id"],
            data["file_format"],
            data["is_album"],
            "зачем",  # TODO: random phrases,
            data["menu"]
        )


@dp.message_handler(state=CreateDemotivator.provide_text)
async def process_text(message: types.Message, state: FSMContext):
    """Use custom user's text in demotivator"""
    if not message.text:
        return await message.reply("Пожалуйста, укажите комментарий для демика.")
    elif len(message.text) > 32:
        return await message.reply("Комментарий должен быть меньше 32 символов.")

    async with state.proxy() as data:
        await state.finish()

        # noqa, refactor

        await process_media(
            message, state,
            data["file_id"],
            data["file_format"],
            data["is_album"],
            message.text,
            data["menu"]
        )


@dp.message_handler(content_types=types.ContentType.PHOTO)
@dp.throttled(rate=2)  # throttling for reliability
async def process_photo(message: types.Message, state: FSMContext):
    """Process photo message"""
    file_id = message.photo[-1].file_id  # highest quality photo (last item in list)
    await process_media(
        message, state,
        file_id, "jpg",
        message.media_group_id,  # can be None
        message.caption  # message.text becomes message.caption when media content present
    )


@dp.message_handler(content_types=[types.ContentType.VIDEO,
                                   types.ContentType.ANIMATION])
@dp.throttled(rate=2)  # throttling for reliability
async def process_video(message: types.Message, state: FSMContext):
    """Process video/gif message"""
    file_id = message[message.content_type].file_id
    await process_media(
        message, state,
        file_id, "mp4",
        message.media_group_id,  # can be None
        message.caption  # message.text becomes message.caption when media content present
    )
