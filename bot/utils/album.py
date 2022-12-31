import asyncio
from typing import Dict, Any

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


# вдохновлено: https://ru.stackoverflow.com/q/1394009/271437
# собирает медиа в один альбом, предотвращая размножение сообщений на каждое вложение
class MediaMergeMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self):
        super(MediaMergeMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: Dict[str, Any]):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler
        except KeyError:
            # всё это чудо работает за счёт задержки между сообщениями в медиа группе
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(0.05)

            data["album"] = self.album_data[message.media_group_id]
            del self.album_data[message.media_group_id]  # TODO: вынести в on_post_process_message
