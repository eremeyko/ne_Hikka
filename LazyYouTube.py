__version__ = (1, 8, 0)
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

import asyncio
import logging
from ast import literal_eval

from .. import utils, loader
from aiohttp import ClientSession
from typing import Optional
from ..tl_cache import CustomTelegramClient  # type: ignore
from ..database import Database  # type: ignore

from hikkatl.errors import YouBlockedUserError
from hikkatl.functions import messages
from hikkatl.types import (
    Message,
    PeerUser,
    InputMessagesFilterEmpty,
    TypeInputPeer,
)
from telethon import events

logger = logging.getLogger(f"LazyYT | {__version__}")

UPDATE_URL: str = (
    "https://raw.githubusercontent.com/eremeyko/ne_Hikka/refs/heads/master/LazyYouTube.py"
)


@loader.tds
class LazyYT(loader.Module):
    """Download video from YouTube with bot @Gozilla_bot"""

    strings = {
        "name": "LazyYouTube",
        "blocked": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>You has blocked the bot @Gozilla_bot!</b>\n"
            "Unblock the bot and try again later"
        ),
        "no_link": "<emoji document_id=5220197908342648622>❗️</emoji> <b>No URL specified!</b>",
        "no_video": (
            "<emoji document_id=5219901967916084166>💥</emoji><b>Unfortunately,"
            "it was not possible to get the video.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Here\'s Your <a href="{link}">video:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Quality: </b>{quality} | "
            "<emoji document_id=5247213725080890199>©️</emoji> <b>Author: </b>{author}"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji><b>Unfortunately,"
            "it was not possible to get the audio.</b>"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Here\'s Your <a href="{link}">audio:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>©️</emoji> <b>Author: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Search your video...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Search your audio...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> New version "
            "update available: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> To update, use: "
            "<code>.dlm {url}</code>"
        ),
    }

    strings_ru = {
        "name": "LazyYouTube",
        "blocked": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Вы заблокировали бота @Gozilla_bot!</b>\n"
            "Разблокируйте бота и повторите запрос ещё раз"
        ),
        "no_link": "<emoji document_id=5220197908342648622>❗️</emoji> <b>Не задано URL!</b>",
        "no_video": (
            "<emoji document_id=5219901967916084166>💥</emoji>"
            "<b>К сожалению, не удалось получить видео.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Вот Ваше <a href="{link}">видео:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Качество: </b>{quality} | "
            "<emoji document_id=5247213725080890199>©️</emoji> <b>Автор: </b>{author}"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji>"
            "<b>К сожалению, не удалось получить аудио.</b>"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Вот Ваше <a href="{link}">аудио:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>©️</emoji> <b>Автор: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Идёт поиск видео...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Идёт поиск аудио...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Доступно "
            "обновление до версии: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Для обновления "
            "используйте: <code>.dlm {url}</code>"
        ),
        "_cls_doc": "Модуль для загрузки видео и аудио из Ютуба с помощью бота @Gozilla_bot",
    }

    def __init__(self) -> None:
        self.update_message: str = ""

        self.current_video_name: str = ""
        self.current_video_quality: str = ""
        self.current_video_author: str = ""

        self.gozilla_bot_username: str = "Gozilla_bot"
        self.gozilla_bot_id: int = None

    @loader.loop(interval=10800, autostart=True, wait_before=False)
    async def check_for_updates(self) -> None:
        try:
            logger.info("[LazyYouTube | Update Checker] Проверка...")
            async with ClientSession() as session:
                async with session.get(UPDATE_URL) as response:
                    new_version_str = await response.text()
                    new_version_str = new_version_str.split("\n")[0]
                    if new_version_str.startswith("__version__"):
                        version_tuple = literal_eval(
                            new_version_str.split("=")[1].strip()
                        )
                        new_version = tuple(map(int, version_tuple))
                        if new_version > __version__:
                            self.update_message = self.strings[
                                "update_available"
                            ].format(
                                version=".".join(map(str, new_version)), url=UPDATE_URL
                            )
                            logger.info(
                                f"[LAzyYouTube] Новая версия обнаружена! {new_version} \n"
                                "Пробую обновиться сам..."
                            )

                            await self.invoke("dlmod", UPDATE_URL, peer=self.logchat)
                        else:
                            self.update_message = ""
        except Exception as e:
            await logger.exception(f"Ошибка проверки обновления: {e}")

    async def client_ready(self, client: CustomTelegramClient, db: Database) -> None:
        self.client: CustomTelegramClient = client
        self.gozilla_bot: TypeInputPeer = await self.client.get_entity(
            self.gozilla_bot_username
        )
        self.gozilla_bot_id: int = self.gozilla_bot.id

        history = await self.client(
            messages.SearchRequest(
                peer=self.gozilla_bot,
                q=" ",
                filter=InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_id=0,
                add_offset=0,
                limit=0,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )

        if not hasattr(history, "count"):
            await self.client.send_message(entity=self.gozilla_bot, message="/start")
            await utils.dnd(self.client, peer=PeerUser(841589476), archive=False)

    async def _find_by_url(self, name: str, mp3: bool = False) -> Optional[Message]:
        m_audio: Optional[Message] = None
        m_video: Optional[Message] = None
        e_trigger = asyncio.Event()

        to_bot = await self.client.send_message(self.gozilla_bot, name)

        async def get_quality_handler(event: events.NewMessage.Event) -> None:
            try:
                if event.message.from_id == self.gozilla_bot_id:
                    if event.message.photo and event.message.reply_markup:
                        buttons = event.message.reply_markup.rows[-2].buttons
                        self.current_video_name = event.message.text.split("\n")[0]
                        self.current_video_quality = buttons[0].text.split("-")[0][2:]
                        self.current_video_author = event.message.text.split("\n")[3][
                            2:
                        ]
                        if len(buttons):
                            await event.message.click((-2 if not mp3 else -1), 0)
            except Exception as e:
                logger.exception(f"[LazyYouTube] Ошибка при получении видео:\n{e}")

        async def get_video_handler(event: events.NewMessage.Event) -> None:
            nonlocal m_video, m_audio, mp3
            if event.message.from_id == self.gozilla_bot_id:
                if mp3:
                    if event.message.audio:
                        m_audio = event.message
                if event.message.video:
                    m_video = event.message
                e_trigger.set()

        self.client.add_event_handler(
            get_quality_handler,
            events.NewMessage(incoming=True, chats=self.gozilla_bot_id),
        )
        self.client.add_event_handler(
            get_video_handler,
            events.NewMessage(incoming=True, chats=self.gozilla_bot_id),
        )

        try:
            await asyncio.wait_for(e_trigger.wait(), timeout=600)
        except asyncio.TimeoutError:
            await to_bot.delete()
            m_video = None
            m_audio = None
        finally:
            self.client.remove_event_handler(get_quality_handler)
            self.client.remove_event_handler(get_video_handler)

        return m_audio if mp3 else m_video

    @loader.command(ru_doc="[ссылка] - Скачивает видео из Ютуба", alias="ют")
    async def yt(self, message: Message) -> None:
        """[url] - Downloading video from YouTube"""
        reply_to: Optional[Message] = await message.get_reply_message()
        args: str = utils.get_args_raw(message)
        query: str = ""
        if not args and not reply_to:
            await utils.answer(message, self.strings["no_link"] + self.update_message)
            return
        try:
            query = (
                reply_to.text
                if reply_to is not None
                and (("youtube" in reply_to.text) or ("youtu" in reply_to.text))
                else args
            )
            m = await utils.answer(
                message, self.strings["searching_video"] + self.update_message
            )
            video = await self._find_by_url(query)
        except YouBlockedUserError:
            await utils.answer(message, self.strings["blocked"] + self.update_message)
            return
        if not video:
            await utils.answer(message, self.strings["no_video"] + self.update_message)
            return
        await utils.answer_file(
            m,
            video,
            caption=(self.strings["your_video"] + self.update_message).format(
                link=query,
                name=self.current_video_name,
                quality=self.current_video_quality,
                author=self.current_video_author,
            ),
            reply_to=reply_to,
        )
        await m.delete()
        return

    @loader.command(ru_doc="[ссылка] - Скачивает музыку из Ютуба", alias="ютм")
    async def ytm(self, message: Message) -> None:
        """[url] - Downloading audio from YouTube"""
        reply_to: Optional[Message] = await message.get_reply_message()
        args: str = utils.get_args_raw(message)
        query: str = ""
        if not args and not reply_to:
            await utils.answer(message, self.strings["no_link"] + self.update_message)
            return

        try:
            query = (
                reply_to.text
                if reply_to is not None
                and (("youtube" in reply_to.text) or ("youtu" in reply_to.text))
                else args
            )
            m = await utils.answer(
                message, self.strings["searching_audio"] + self.update_message
            )
            audio = await self._find_by_url(query, True)
        except YouBlockedUserError:
            await utils.answer(message, self.strings["blocked"] + self.update_message)
            return
        if not audio:
            await utils.answer(message, self.strings["no_audio"] + self.update_message)
            return
        await utils.answer_file(
            m,
            audio,
            caption=(self.strings["your_audio"] + self.update_message).format(
                link=query,
                name=self.current_video_name,
                author=self.current_video_author,
            ),
            reply_to=reply_to,
        )
        await m.delete()
        return
