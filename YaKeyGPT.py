__version__ = (1, 2, 8)
# meta developer: @eremod
#       
#
#	.----..----. .----..-.   .-. .----. .----. 
#	| {_  | {}  }| {_  |  `.'  |/  {}  \| {}  \
#	| {__ | .-. \| {__ | |\ /| |\      /|     /
#	`----'`-' `-'`----'`-' ` `-' `----' `----' 
#
#              	© Copyright 2024
#          	https://t.me/eremod
#
# 🔒      Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html
# Original repository: https://github.com/eremeyko/ne_Hikka

import aiohttp
import json
from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class YaKeyGPT(loader.Module):
    """🤖 YaKeyGPT - автоматическое исправление сообщений"""

    strings_ru = {
        "name": "YaKeyGPT",
        "no_response": "<emoji document_id=5226660202035554522>✖️</emoji> Ошибка: нет текста для исправления.",
        "ya_set_fix": "Методы исправления не были указаны, установлен метод по умолчанию: fix.",
        "auto_fix_enabled": "<emoji document_id=5188216731453103384>✔️</emoji> Автоисправление включено с методами: {}.",
        "auto_fix_disabled": "<emoji document_id=5226660202035554522>✖️</emoji> Автоисправление выключено.",
    }

    strings_ = {
        "name": "YaKeyGPT",
		"no_response": "<emoji document_id=5226660202035554522>✖️</emoji> Error: no text to correct.",
		"ya_set_fix": "No fix methods were specified, default method set: fix.",
		"auto_fix_enabled": "<emoji document_id=5188216731453103384>✔️</emoji> Auto-correction is enabled with methods: {}.",
		"auto_fix_disabled": "<emoji document_id=5226660202035554522>✖️</emoji> Auto-correction is disabled.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_methods",
                ["fix", "emoji"],
                "Методы исправления текста",
                validator=loader.validators.MultiChoice(["rewrite", "fix", "emoji"]),
            ),
        )
    
    async def client_ready(self, client, db):
    	self.client = client
    	self.prefix = self.get_prefix()

    async def send_request(self, method, text):
        url = f"https://keyboard.yandex.net/gpt/{method}"
        payload = json.dumps({"text": text})
        headers = {
            'User-Agent': "okhttp/4.12.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=utf-8"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                return await response.json()

    async def process_command(self, method, message: Message):
        reply = await message.get_reply_message()
        text_to_correct = reply.text if reply else message.text.split(maxsplit=1)[1] if message.text.startswith(".") else message.text

        response_data = await self.send_request(method, text_to_correct)
        return response_data.get("response", self.strings["no_response"])

    @loader.command(ru_doc="<ответ/текст> — Быстро исправляет текст")
    async def qfix(self, message: Message):
        """<answer/text> — Quickly corrects text."""
        corrected_text = await self.process_command("fix", message)
        await utils.answer(message, corrected_text)

    @loader.command(ru_doc="<ответ/текст> — Быстро перепишет текст")
    async def qrewrite(self, message: Message):
        """<answer/text> - Will quickly rewrite the text."""
        corrected_text = await self.process_command("rewrite", message)
        await utils.answer(message, corrected_text)

    @loader.command(ru_doc="<ответ/текст> — Добавит эмодзи на твой текст😊")
    async def qemoji(self, message: Message):
        """ <answer/text> — Will add emoji to your text😊."""
        corrected_text = await self.process_command("emoji", message)
        await utils.answer(message, corrected_text)


    @loader.command(ru_doc=" — Включает или выключает методы исправления.")
    async def yaset(self, message: Message):
        """ — Enables or disables correction methods."""
        state = not self.get("yatext", False)
        self.set("yatext", state)
    
        if not self.config["auto_methods"]:
            self.config["auto_methods"] = ["fix"]
            await utils.answer(message, self.strings["ya_set_fix"])
            return
    
        if state:
            status_message = self.strings["auto_fix_enabled"].format(", ".join(self.config["auto_methods"]))
        else:
            status_message = self.strings["auto_fix_disabled"]
    
        await utils.answer(message, status_message)


    async def watcher(self, message: Message):
        if not self.get("yatext", False):
            return
    
        if message.out:
            text = message.text
            if text.startswith(self.prefix):
            	return
            methods = self.config["auto_methods"]

            for method in methods:
                response_data = await self.send_request(method, text)
                text = response_data.get("response", self.strings["no_response"])
            
            await utils.answer(message, text)
