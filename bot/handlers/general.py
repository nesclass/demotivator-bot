from aiogram import types

from bot import dp


@dp.message_handler()
async def general(message: types.Message):
    return await message.reply("Поддерживается создание демиков из картинок, гифок и видео "
                               "<i>(максимальный вес файла: 20 МБ)</i>.\n\n"

                               "Текстовый ввод реализован лишь для <b>однострочных комментариев</b>, "
                               "временно не реализовано уменьшение размера шрифта для длинного текста.\n\n"
                               
                               "Исходный код: https://github.com/nesclass/demotivator-bot",

                               disable_web_page_preview=True)
