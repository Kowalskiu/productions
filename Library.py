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

    async def init(self):
        """Инициализирует библиотеку."""
        self.loaded_classes = {}
        await self._init_classes()  # Теперь utils создаётся здесь

    async def _init_classes(self):
        """Инициализирует все классы библиотеки."""
        self.utils = KowaWorkTran(self)  # Создаём объект utils
        self.loaded_classes["utils"] = self.utils

    # ... остальной код ...


#─────────────────────────────────────

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

#─────────────────────────────────────

class KowaWorkTran(loader.Module):
    """This class is used to handle all the utility functions of the library."""

    def __init__(self, lib: loader.Library,):
        self.lib = lib
        self._db = lib.db
        self._client = lib.client
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

    async def _refresh_lib(self, lib: loader.Library,):
        """do not use this method directly! Refreshes the class with the current state of the library :param lib: The library class :return: None"""
        self.lib = lib
        self.utils = lib.utils
        return self


    def get_str(self, string: str, all_strings: dict, message: Optional[Message] = None) -> str:
        """Get a string from a dictionary :param string: The string to get: param all_strings: The dictionary to get the string from: param message: The message to check for forced chat strings: return: The translated string"""
        base_strings = "strings"
        default_lang = None
        if (
            "translations" in self._db
            and "lang" in self._db["translations"]
        ):
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
        if (
            default_lang
            and default_lang in list(languages)
            and string in languages[default_lang]
        ):
            return languages[default_lang][string].replace("<br>", "\n")
        return all_strings[base_strings][string].replace("<br>", "\n")