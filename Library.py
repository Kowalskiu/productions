from telethon import events
from telethon.types import Message
from .. import loader

class BoostWorkLib(loader.Library):
    '''Lib for modules to speed up work'''
    developer = "@Kowalskiu"


    def __init__(self):
        self.config = loader.LibraryConfig(
            loader.ConfigValue(
                "enabled",
                True,
                lambda: "Включить/Выключить BoostWorkLib",
                validator=loader.validators.Boolean(),
            ),
        )

    def init(self):
        self.cache = {}  # Кэш для хранения результатов
        if self.config["enabled"]:
            self.log.info("BoostWorkLib включен")
        else:
            self.log.info("BoostWorkLib выключен")

    async def get_message(self, chat_id, message_id):
        """Получает сообщения с кэшированием"""
        if not self.config["enabled"]:
            return await self.client.get_messages(chat_id, ids=message_id)

        key = f"{chat_id}:{message_id}"

        # Проверяет наличия сообщения в кэше
        if key in self.cache:
            return self.cache[key]

        # Если сообщение не в кэше выполняется запрос
        message = await self.client.get_messages(chat_id, ids=message_id)

        # Сохраняем сообщение в кэше
        self.cache[key] = message

        return message

    async def send_message(self, chat_id, message, **kwargs):
        """Отправляет сообщения с использованием кэширования результата"""
        if not self.config["enabled"]:
            try:
                response = await self.client.send_message(chat_id, message, **kwargs)
                return response
            except Exception as e:
                self.log.error(f"Failed to send message: {str(e)}")
                return None

        try:
            response = await self.client.send_message(chat_id, message, **kwargs)
            return response
        except Exception as e:
            self.log.error(f"Failed to send message: {str(e)}")
            return None

    def clear_cache(self):
        """Очищает кэша"""
        self.cache.clear()
