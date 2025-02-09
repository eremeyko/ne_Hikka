__version__ = (1, 4, 1)
# meta developer: @eremod
#
#
# 	.----..----. .----..-.   .-. .----. .----.
# 	| {_  | {}  }| {_  |  `.'  |/  {}  \| {}  \
# 	| {__ | .-. \| {__ | |\ /| |\      /|     /
# 	`----'`-' `-'`----'`-' ` `-' `----' `----'
#
#              	© Copyright 2024
#          	https://t.me/eremod
#
# 🔒      Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html
# Original repository: https://github.com/eremeyko/ne_Hikka

from aiohttp import ClientSession
from json import dumps
from hikkatl.types import Message  # type: ignore
from .. import loader, utils
import logging
from ast import literal_eval

UPDATE_URL = "https://github.com/eremeyko/ne_Hikka/raw/master/YaKeyGPT.py"
logger = logging.getLogger(__name__)


@loader.tds
class YaKeyGPT(loader.Module):
    """🤖 YaKeyGPT - автоматическое исправление сообщений"""

    strings_ru = {
        "name": "YaKeyGPT",
        "no_response": "<emoji document_id=5226660202035554522>✖️</emoji> Ошибка: нет текста для исправления.",
        "ya_set_fix": "Методы исправления не были указаны, установлен метод по умолчанию: fix.",
        "auto_fix_enabled": "<emoji document_id=5188216731453103384>✔️</emoji> Автоисправление включено с методами: {}.",
        "auto_fix_disabled": "<emoji document_id=5226660202035554522>✖️</emoji> Автоисправление выключено.",
        "no_text_error": "<emoji document_id=5226660202035554522>✖️</emoji> !!!Ошибка: отсутствует текст или ответ для исправления.",
        "update_available": (
            "<emoji document_id=5771695636411847302>📢</emoji> Доступно "
            "обновление до версии: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Для обновления "
            "используйте: <code>.dlm {url}</code>"
        ),
    }

    strings = {
        "name": "YaKeyGPT",
        "no_response": "<emoji document_id=5226660202035554522>✖️</emoji> Error: no text to correct.",
        "ya_set_fix": "No fix methods were specified, default method set: fix.",
        "auto_fix_enabled": "<emoji document_id=5188216731453103384>✔️</emoji> Auto-correction is enabled with methods: {}.",
        "auto_fix_disabled": "<emoji document_id=5226660202035554522>✖️</emoji> Auto-correction is disabled.",
        "no_text_error": "<emoji document_id=5226660202035554522>✖️</emoji> Error: no text or reply to correct.",
        "update_available": (
            "<emoji document_id=5771695636411847302>📢</emoji> Available "
            "update to version: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> To update "
            "use: <code>.dlm {url}</code>"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_methods",
                ["fix", "emoji"],
                "Методы исправления текста",
                validator=loader.validators.MultiChoice(["fix", "rewrite", "emoji"]),
            ),
        )

        self.update_message: str = ""
        self.logchat: int = 0

    async def client_ready(self, client, db):
        self.client = client
        self.prefix = self.get_prefix()
        logging.basicConfig(
            level=logging.DEBUG if self.config["_logger"] else logging.ERROR
        )
        logger.debug(f"[YaKeyGPT] успешно включено")
        self.logchat = next(
            filter(
                None,
                [
                    d.id if d.title == "hikka-logs" or "heroku-logs" else ""
                    async for d in self.client.iter_dialogs()
                ],
            )
        )

    @loader.loop(interval=10800, autostart=True, wait_before=False)
    async def check_for_updates(self) -> None:
        try:
            if not self.config["check_updates"]:
                return
            logger.info("[YaKeyGPT | Update Checker] Checking for updates...")
            async with ClientSession() as session:
                async with session.get(UPDATE_URL) as response:
                    new_version_str = await response.text()
                    new_version_str = new_version_str.splitlines()[0].split("=")[1]
                    version_tuple = literal_eval(new_version_str)
                    if version_tuple > __version__:
                        self.update_message = self.strings["update_available"].format(
                            version=".".join(map(str, version_tuple)), url=UPDATE_URL
                        )
                        logger.info(
                            f"[YaKeyGPT] New version available! {version_tuple}\n"
                            "Trying to update..."
                        )
                        await self.invoke("dlmod", UPDATE_URL, peer=self.logchat)
                    else:
                        self.update_message = ""
        except Exception as e:
            logger.exception(f"Error in update checker: {e}")

    async def send_request(self, method, text):
        url = f"https://keyboard.yandex.net/gpt/{method}"
        payload = dumps({"text": text})
        headers = {
            "User-Agent": "okhttp/4.12.0",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json; charset=utf-8",
        }

        async with ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                return await response.json()

    async def process_command(self, method, message: Message):
        reply = await message.get_reply_message()
        text_to_correct = reply.message if reply else utils.get_args_raw(message)

        if not text_to_correct:
            await utils.answer(
                message, self.strings["no_text_error"] + f"\n\n{self.update_message}"
            )
            return None

        response_data = await self.send_request(method, text_to_correct)
        return response_data.get(
            "response", self.strings["no_response"] + f"\n\n{self.update_message}"
        )

    @loader.command(ru_doc="<ответ/текст> — Быстро исправляет текст")
    async def qfix(self, message: Message):
        """<answer/text> — Quickly corrects text."""
        corrected_text = await self.process_command("fix", message)
        if corrected_text:
            await utils.answer(message, corrected_text)

    @loader.command(ru_doc="<ответ/текст> — Быстро перепишет текст")
    async def qrewrite(self, message: Message):
        """<answer/text> - Quikly rewrite text."""
        corrected_text = await self.process_command("rewrite", message)
        if corrected_text:
            await utils.answer(message, corrected_text)

    @loader.command(ru_doc="<ответ/текст> — Добавит эмодзи на твой текст😊")
    async def qemoji(self, message: Message):
        """<answer/text> — Quickly adds an emoji to text😊"""
        corrected_text = await self.process_command("emoji", message)
        if corrected_text:
            await utils.answer(message, corrected_text)

    @loader.command(ru_doc=" — Включает или выключает методы исправления.")
    async def yaset(self, message: Message):
        """— Enables or disables correction methods."""
        state = not self.get("yatext", False)
        self.set("yatext", state)

        if not self.config["auto_methods"]:
            self.config["auto_methods"] = ["fix"]
            await utils.answer(
                message, self.strings["ya_set_fix"] + f"\n\n{self.update_message}"
            )
            return

        if state:
            status_message = (
                self.strings["auto_fix_enabled"] + f"\n\n{self.update_message}"
            ).format(", ".join(self.config["auto_methods"]))
        else:
            status_message = (
                self.strings["auto_fix_disabled"] + f"\n\n{self.update_message}"
            )

        await utils.answer(message, status_message)

    async def watcher(self, message: Message):
        if not self.get("yatext", False):
            return
        if (
            message.forward
            or message.post
            or getattr(message, "from_scheduled", False)
            or not message.out
            or message.text.startswith(self.prefix)
        ):
            return

        text = message.text
        methods_order = ["fix", "rewrite", "emoji"]
        auto_methods = self.config["auto_methods"]

        enabled_methods = [method for method in methods_order if method in auto_methods]

        for method in enabled_methods:
            response_data = await self.send_request(method, text)
            text = response_data.get("response", self.strings["no_response"])

        await utils.answer(message, text)
