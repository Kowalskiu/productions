
import re
import aiohttp
import asyncio
import os

from typing import Optional, Dict, An

from telethon import events
from telethon.types import Message
from .. import loader

class KowaWorkLib(loader.Library):
    '''Lib for modules Kowalskiu'''
    developer = "@Kowalskiu"

    def __init__(self):
        self.cache = {}  # Кэш для хранения результатов

    def get_message(self, chat_id, message_id):
        """Получает сообщения с кэшированием"""
        key = f"{chat_id}:{message_id}"
        
        # Проверяет наличия сообщения в кэше
        if key in self.cache:
            return self.cache[key]

        # Если сообщение не в кэше выполняется запрос
        message = self.client.get_messages(chat_id, ids=message_id)
        
        # Сохраняем сообщение в кэше
        self.cache[key] = message
        
        return message

    async def send_message(self, chat_id, message, **kwargs):
        """Отправляет сообщения с использованием кэширования результата"""
        try:
            response = await self.client.send_message(chat_id, message, **kwargs)
            return response
        except Exception as e:
            self.log.error(f"Failed to send message: {str(e)}")
            return None

    def clear_cache(self):
        """Очищает кэша"""
        self.cache.clear()


    @staticmethod
    def convert_size(size):
        """Convert file size to human-readable format."""
        power = 2**10
        n = 0
        units = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
        while size > power:
            size /= power
            n += 1
        return round(size, 2), units[n]

    async def upload_to_envs(self, path):
        """Upload file to envs.sh and return the URL."""
        url = "https://envs.sh"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={"file": open(path, "rb")}) as response:
                if response.status != 200:
                    os.remove(path)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=await response.text(),
                        headers=response.headers,
                    )
                result = await response.text()

                os.remove(path)
                return result