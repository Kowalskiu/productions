import ast
import asyncio
import collections
import contextlib
import copy
import hashlib
import html
import io
import logging
import math
import re
from datetime import datetime, timedelta
from typing import IO, Any, Optional, Tuple, Union

import aiohttp
import grapheme
import requests
from aiogram.types import ChatPermissions
from aiogram.utils.exceptions import (
    BotKicked,
    ChatNotFound,
    MessageCantBeDeleted,
    MessageToDeleteNotFound,
)
from telethon.errors import UserNotParticipantError
from telethon.hints import EntityLike
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    EditAdminRequest,
    EditBannedRequest,
    GetFullChannelRequest,
    InviteToChannelRequest,
)
from telethon.tl.functions.messages import (
    GetDialogFiltersRequest,
    UpdateDialogFilterRequest,
)
from telethon.tl.types import (
    Channel,
    Chat,
    ChatAdminRights,
    ChatBannedRights,
    Message,
    MessageEntityUrl,
    User,
)
import aiohttp
import asyncio
import os
from telethon import events
from telethon.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

class KowaWorkLib(loader.Library):
    '''Библиотека для модулей Kowalskiu'''
    developer = "@Kowalskiu"

    def __init__(self):
        """Инициализирует библиотеку."""
        super().__init__()
        self.loaded_classes = {}
        self.utils = None  # Инициализируем как None, затем заполняем в init

    async def init(self, db, client, inline):
        """Инициализирует библиотеку с необходимыми атрибутами."""
        self._db = db
        self._client = client
        self.inline = inline
        self.utils = KowaWorkTran(self)  # Теперь передаем self с инициализированными атрибутами
        self.loaded_classes["utils"] = self.utils
        await self.__refresh_classes()

    async def __refresh_classes(self):
        """Обновляет все классы библиотеки."""
        if self.utils:
            self.utils.log(
                logging.DEBUG,
                self.__class__.__name__,
                "Refreshing all classes to the current library state.",
                debug_msg=True,
            )
        
        for cl in self.loaded_classes:
            if self.utils:
                self.utils.log(
                    logging.DEBUG,
                    self.__class__.__name__,
                    f"Refreshing {cl} to the current library state.",
                    debug_msg=True,
                )
            self.loaded_classes[cl] = await self.loaded_classes[cl]._refresh_lib(self)
            if getattr(self, cl):
                setattr(self, cl, self.loaded_classes[cl])
        
        if self.utils:
            self.utils.log(
                logging.DEBUG,
                self.__class__.__name__,
                "Refreshing of all classes done.",
                debug_msg=True,
            )

    @staticmethod
    def convert_size(size):
        """Конвертирует размер файла в читаемый формат."""
        power = 2**10
        n = 0
        units = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
        while size > power:
            size /= power
            n += 1
        return round(size, 2), units[n]

    async def upload_to_envs(self, path):
        """Загружает файл на envs.sh и возвращает URL."""
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

class KowaWorkTran(loader.Module):
    """Класс для обработки утилитарных функций библиотеки."""

    def __init__(self, lib: loader.Library):
        if not hasattr(lib, '_db'):
            raise AttributeError("Library object must have '_db' attribute")
        
        self.lib = lib
        self._db = lib._db
        self._client = lib._client
        self.inline = lib.inline
        self._libclassname = lib.__class__.__name__
        self._lib_db = self._db.setdefault(self._libclassname, {})
        self._chats_db = self._lib_db.setdefault("chats", {})
        self._perms_cache = {}
        self._get_fullchannelrequest_cache = {}
        
        self.log(
            logging.DEBUG,
            self._libclassname,
            f"class {self.__class__.__name__} is being initiated!",
            debug_msg=True,
        )

    async def _refresh_lib(self, lib: loader.Library):
        """Обновляет класс текущим состоянием библиотеки."""
        self.lib = lib
        self._db = lib._db
        self._client = lib._client
        self.inline = lib.inline
        return self

    def get_str(self, string: str, all_strings: dict, message: Optional[Message] = None) -> str:
        """Получает строку из словаря."""
        base_strings = "strings"
        default_lang = None
        
        if "translations" in self._db and "lang" in self._db["translations"]:
            default_lang = self._db["translations"]["lang"]
            
        languages = {base_strings: all_strings[base_strings]}
        
        for lang in all_strings:
            if len(lang.split("_", 1)) == 2:
                languages[lang.split("_", 1)[1]] = {
                    **all_strings[base_strings],
                    **all_strings[lang],
                }
                
        if message:
            if chat_id := utils.get_chat_id(message):
                chatid_db = self._chats_db.setdefault(str(chat_id), {})
                forced_lang = chatid_db.get("forced_lang")
                for lang, strings in languages.items():
                    if lang and forced_lang == lang:
                        if string in strings:
                            return strings[string].replace("<br>", "\n")
                        break
                        
        if (default_lang and default_lang in list(languages) 
            and string in languages[default_lang]):
            return languages[default_lang][string].replace("<br>", "\n")
            
        return all_strings[base_strings][string].replace("<br>", "\n")