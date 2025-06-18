from telethon import events
from telethon.types import Message
from .. import loader

class BoostWorkLib(loader.Library):
    '''Lib for modules to speed up work'''
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
