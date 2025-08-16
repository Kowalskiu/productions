import aiohttp
import asyncio
import os
from telethon import events
from telethon.types import Message
from .. import loader


class KowaWorkLib(loader.Library):
    '''Lib for modules Kowalskiu'''
    developer = "@Kowalskiu"

    @staticmethod
    async def _load_github(self):
        """
        Downloads the Apo-LibController from GitHub
        """
        link = "https://github.com/Kowalskiu/productions/raw/master/JujutsuKaisen.py"
        async with aiohttp.ClientSession() as session, session.head(link) as response:
            if response.status >= 300:
                return None
        link_message = await self._client.send_message(
            "me", f"{self.lib.get_prefix()}dlmod {link}"
        )
        await self.lib.allmodules.commands["dlmod"](link_message)

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