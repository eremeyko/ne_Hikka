__version__ = (1, 6, 8)

# meta developer: @eremod
# Отдельная благодарность: @stupid_alien_mods
#
#
# 	.----..----. .----..-.   .-. .----. .----.
# 	| {_  | {}  }| {_  |  `.'  |/  {}  \| {}  \
# 	| {__ | .-. \| {__ | |\ /| |\      /|     /
# 	`----'`-' `-'`----'`-' ` `-' `----' `----'
#
#              	© Copyright 2024
#          	   https://t.me/eremod
#
# 🔒      Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html
# Original repository: https://github.com/eremeyko/ne_Hikka

import asyncio
import logging

from .. import loader, utils
from ..tl_cache import CustomTelegramClient  # type: ignore
from ..database import Database  # type: ignore

from telethon import events
from hikkatl.types import Message
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import FloodWaitError

from typing import Optional
from aiohttp import ClientSession
from time import time
from ast import literal_eval

UPDATE_URL = "https://raw.githubusercontent.com/eremeyko/ne_Hikka/refs/heads/master/BIO%20Audio.py"
logger = logging.getLogger(__name__)


@loader.tds
class LastFM(loader.Module):
    strings = {
        "name": "BIOAudio",
        "no_track": "<emoji document_id=5891249688933305846>🎵</emoji> Currently nothing is playing",
        "loading": '🔍 Searching for the track "{name}"...',
        "track_not_found": "<emoji document_id=5778527486270770928>❌</emoji> Track not found: {track}",
        "status_changed": (
            "<emoji document_id=5890997763331591703>🔊"
            "</emoji> Music broadcast status in BIO: {status}"
        ),
        "enabled": "Enabled",
        "disabled": "Disabled",
        "current_play": (
            f"<emoji document_id=5891249688933305846>🎵</emoji> "
            "The track is playing now: <code>{name}</code>"
        ),
        "find_play": (
            "<emoji document_id=5891249688933305846>🎵</emoji> "
            "Track found: <code>{name}</code>"
        ),
        "config_error": (
            "<emoji document_id=5881702736843511327>⚠️</emoji> Please "
            "enter the API key and Username in the config"
        ),
        "update_available": (
            "\n<emoji document_id=5771695636411847302>📢</emoji> Update available to version: "
            "{version}!\n<emoji document_id=5967816500415827773>"
            "💻</emoji> To update, use: <code>.dlm {url}</code>"
        ),
        "stats": (
            "<emoji document_id=5931472654660800739>📊</emoji>  Listening statistics:\n\n"
            "Total tracks: {total}\nLast week: {week}\nLast month: {month}"
        ),
        "count_listened": (
            "<emoji document_id=5994378914636500516>📈</emoji> "
            "<b>Collecting audition statistics...</b>"
        ),
        "error_fmus": "<b><emoji document_id=5881702736843511327>⚠️</emoji> Enter track name!</b>",
        "error_lstats": (
            "<b><emoji document_id=5881702736843511327>⚠️</emoji> "
            "Error while retrieving statistics: {str(e)}</b>"
        ),
        "_cls_doc": "Module for broadcasting playing tracks to Telegram BIO and music search",
    }

    strings_ru = {
        "name": "BIOAudio",
        "no_track": "<emoji document_id=5891249688933305846>🎵</emoji> Сейчас ничего не играет",
        "loading": '🔍 Идет поиск трека "{name}"...',
        "track_not_found": "<emoji document_id=5778527486270770928>❌</emoji> Трек не найден: {track}",
        "status_changed": (
            "<emoji document_id=5890997763331591703>🔊"
            "</emoji> Статус трансляции музыки в БИО: {status}"
        ),
        "enabled": "Включено",
        "disabled": "Выключено",
        "current_play": (
            f"<emoji document_id=5891249688933305846>🎵</emoji> "
            "Сейчас играет: <code>{name}</code>"
        ),
        "find_play": (
            "<emoji document_id=5891249688933305846>🎵</emoji> "
            "Найден трек: <code>{name}</code>"
        ),
        "config_error": (
            "<emoji document_id=5881702736843511327>⚠️</emoji> Пожалуйста, "
            "введите API-ключ и Юзернейм в конфиге"
        ),
        "update_available": (
            "\n<emoji document_id=5771695636411847302>📢</emoji> Доступно обновление до версии: "
            "{version}!\n<emoji document_id=5967816500415827773>"
            "💻</emoji> Для обновления используйте: <code>.dlm {url}</code>"
        ),
        "count_listened": (
            "<emoji document_id=5994378914636500516>📈</emoji> "
            "<b>Собираем статистику прослушиваний...</b>"
        ),
        "stats": (
            "<emoji document_id=5931472654660800739>📊</emoji>  Статистика прослушиваний:\n\n"
            "Всего треков: {total}\nЗа последнюю неделю: {week}\nЗа последний месяц: {month}"
        ),
        "error_fmus": "<b><emoji document_id=5881702736843511327>⚠️</emoji> Введите название трека!</b>",
        "error_lstats": (
            "<emoji document_id=5881702736843511327>⚠️</emoji> "
            "Ошибка при получении статистики: {str(e)}"
        ),
        "_cls_doc": "Модуль для трансляции играющих треков в БИО Telegram и поиска музыки",
    }

    def __init__(self):
        self.logchat: int = 0
        self.db: Optional[Database] = None
        self.client: Optional[CustomTelegramClient] = None

        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                "4d533105ac1d9bf47c6c2237c71d701b",
                "API-ключ Last.fm",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "username",
                "",
                "Ваш username на Last.fm",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "sleep_time",
                [15, 5],
                "Задержка проверки в секундах [без_музыки, с_музыкой]",
                validator=loader.validators.Series(fixed_len=2),
            ),
            loader.ConfigValue(
                "old_bio",
                "",
                "Текст БИО по умолчанию",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "new_bio",
                "🎧 Сейчас играет: {artist} - {title} [💿{album}]",
                "Формат БИО при играющем треке. Доступные параметры: {artist}, {title}, {album}",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "_logger",
                False,
                "Вывод информации для дебага. Используйте только, если понимаете что-то в этом",
                validator=loader.validators.Boolean(),
            ),
        )
        self.audio_status: bool = False
        self.scrobbling_task = None
        self.previous_track: str = ""
        self.msearch: str = ""
        self.update_message: str = ""
        self.old_bio_check: str = ""
        self.check_timeout: int = self.config["sleep_time"][0]
        self.cut: int = 0

    async def client_ready(
        self, client: Optional[CustomTelegramClient], db: Optional[Database]
    ) -> None:
        logging.basicConfig(
            level=logging.DEBUG if self.config["_logger"] else logging.ERROR
        )

        logger.debug(f"[BIO AUDIO] успешно включено")
        self.client = client
        self.db = db

        self.logchat = next(
            filter(
                None,
                [
                    d.id if d.title == "hikka-logs" else ""
                    async for d in self.client.iter_dialogs()
                ],
            )
        )

        self.audio_status = self.get("audio_status", False)
        user = await self.client(GetFullUserRequest(self.client.tg_id))
        self.cut = 140 if user.users[0].premium else 70
        self.old_bio_check = user.full_user.about
        logger.debug(f"[BIO AUDIO] статус сейчас: {self.old_bio_check}")
        if self.audio_status and not self.scrobbling_task:
            self.scrobbling_task = asyncio.create_task(self.scrobbling_loop())
        logger.debug(f"[BIO AUDIO] статус скробблинга: {bool(self.scrobbling_task)}")

    async def scrobbling_loop(self) -> None:
        logger.debug(
            f"[BIO AUDIO | цикл скробблинга] аудио статус? - {self.audio_status} - {self.check_timeout}"
        )
        while self.audio_status:
            await self.update_bio()
            await asyncio.sleep(self.check_timeout)

    async def update_bio(self) -> None:
        logger.debug(f"[BIO AUDIO | обновление био] метод запущен")
        try:
            track_info = await self.playing_now(self.config["username"])
            if track_info:
                logger.debug(f"[BIO AUDIO | обновление био] инфа о треке получена")
                self.check_timeout = self.config["sleep_time"][1]
                current_track = self.config["new_bio"].format(**track_info)
                self.msearch = f"{track_info['artist']} - {track_info['title']}"
                logger.debug(
                    f"[BIO AUDIO | обновление био] сейчас играет - {current_track}"
                )
                if self.previous_track != current_track:
                    logger.debug(
                        f"[BIO AUDIO | обновление био] Условие в цикле, треки разные"
                    )
                    await self.client(
                        UpdateProfileRequest(about=current_track[: self.cut])
                    )
                    self.previous_track = current_track
                    logger.debug(
                        f"[BIO AUDIO | обновление био] био обновлено на новый трек "
                    )
            else:
                logger.debug(f"[BIO AUDIO | обновление био] информации о треке нет ")
                self.check_timeout = self.config["sleep_time"][0]
                user = await self._client(GetFullUserRequest(self._client.tg_id))
                if user.full_user.about != self.config["old_bio"]:
                    logger.debug(
                        f"[BIO AUDIO | обновление био] обнаружен трек в статусе, но ничего не играет"
                    )
                    await self.client(
                        UpdateProfileRequest(about=self.config["old_bio"][: self.cut])
                    )
                    self.msearch = ""
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"[BIO AUDIO] Ошибка в update_bio: {e}")

    async def _request(self, method: str, **kwargs) -> dict | bool:
        params = {
            "method": method,
            "format": "json",
            "api_key": self.config["api_key"],
            **kwargs,
        }
        if method == "user.getrecenttracks":
            params["limit"] = 1

        async with ClientSession() as session:
            async with session.get(
                "https://ws.audioscrobbler.com/2.0/", params=params
            ) as response:
                try:
                    data = await response.json()
                    if "error" in data and data["error"] == 6:
                        return False
                    return data
                except Exception as e:
                    logger.error(f"[BIO AUDIO] Ошибка при запросе: {e}")
                    return False

    async def playing_now(self, user: str) -> dict | bool:
        request = await self._request("user.getrecenttracks", user=user)
        if request is False:
            return False

        recent_track = request["recenttracks"]["track"][0]
        if (
            "@attr" in recent_track
            and recent_track["@attr"].get("nowplaying") == "true"
        ):
            return {
                "artist": recent_track["artist"]["#text"],
                "title": recent_track["name"],
                "album": recent_track["album"]["#text"],
            }
        return {}

    @loader.loop(interval=10800, autostart=True, wait_before=False)
    async def check_for_updates(self):
        try:
            logger.debug(f"[BIO AUDIO | проверка обновы] Проверка...")
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
                            logger.debug(
                                f"[BIO AUDIO] Новая версия обнаружена! {new_version} \n"
                                "Пробую обновиться сам..."
                            )

                            await self.invoke("dlmod", UPDATE_URL, peer=self.logchat)
                        else:
                            self.update_message = ""
        except Exception as e:
            logger.error(f"Ошибка проверки обновления: {e}")

    async def _find_music(self, name: str) -> Optional[Message]:
        music: Optional[Message] = None
        e_trigger = asyncio.Event()
        initial_musics: Optional[list] = await self.client.inline_query(
            "murglar_bot", name
        )

        def filter_services(musics, exclude: tuple = ()):
            name_of_services: dict = {}
            for mus in musics:
                service_name = mus.description.split(" - ")[1]
                if service_name not in exclude:
                    name_of_services[service_name] = mus
            return name_of_services

        services = filter_services(initial_musics, exclude=("Deezer", "SberZvuk"))
        if not services:
            logger.warning("[BIOAudio | _find_music] Нет доступных сервисов.")
            return None

        service_names = list(services.keys())
        current_service: int = 0

        m = await services[service_names[current_service]].click(self.logchat)

        @self.client.on(events.MessageEdited(chats=self.logchat))
        async def get_audio(event: events.MessageEdited.Event) -> None:
            nonlocal music, m, current_service, service_names, services
            try:
                if event.message.id == m.id:
                    if "Сорри, произошла ошибка: " in event.message.text:
                        await m.delete()
                        current_service = 1

                        if services:
                            m = await services[service_names[current_service]].click(
                                self.logchat
                            )
                        else:
                            e_trigger.set()
                        return

                    if event.message.document and not getattr(
                        event.message, "reply_markup", None
                    ):
                        music = event.message.document
                        e_trigger.set()
                        raise events.StopPropagation
            except events.StopPropagation:
                raise
            except Exception as ga:
                logger.exception(f"[BIOAudio | get_audio] Ошибка:\n{ga}")

        try:
            await asyncio.wait_for(e_trigger.wait(), timeout=135)
        except asyncio.TimeoutError:
            logger.warning("[BIOAudio | _find_music] Время ожидания истекло.")
        except Exception as e:
            await m.delete()
            logger.exception(f"[BIOAudio | _find_music] Ошибка:\n{e}")
            music = None
        else:
            await m.delete()
        finally:
            self.client.remove_event_handler(get_audio, events.MessageEdited)

        return music

    @loader.command(ru_doc="[название] - Поиск трека по названию", alias="нмуз")
    async def fmus(self, message: Message):
        """[name] - Search for a track by title"""
        reply_to = getattr(message, "reply_to_msg_id", utils.get_topic(message))
        name = utils.get_args_raw(message)
        if not name:
            await utils.answer(message, self.strings["error_fmus"])
            return
        m_req = await utils.answer(message, self.strings["loading"].format(name=name))
        music = await self._find_music(name)
        if not music:
            await utils.answer(
                message,
                self.strings["track_not_found"].format(track=name)
                + self.update_message,
            )
            return
        await m_req.delete()
        await self.client.send_file(
            message.peer_id,
            music,
            caption=self.strings["find_play"].format(name=name),
            reply_to=reply_to if reply_to else None,
        )

    @loader.command(ru_doc="- Отправить трек, что сейчас играет", alias="смуз")
    async def lmus(self, message: Message):
        """Send the track that's playing right now"""
        reply_to = getattr(message, "reply_to_msg_id", utils.get_topic(message))
        if not self.msearch:
            await utils.answer(
                message, f"<b>{self.strings['no_track']}</b>{self.update_message}"
            )
            return
        m_req = await utils.answer(
            message, self.strings["loading"].format(name=self.msearch)
        )
        try:
            music = await self._find_music(self.msearch)
            if music:
                await m_req.delete()
                await self.client.send_file(
                    message.peer_id,
                    music,
                    caption=self.strings["current_play"].format(name=self.msearch)
                    + self.update_message,
                    reply_to=reply_to if reply_to else None,
                )
            else:
                raise FileNotFoundError("Музыка не найдена")
        except FileNotFoundError as _:
            await utils.answer(
                message,
                self.strings["track_not_found"].format(track=self.msearch)
                + f"\n{self.update_message}",
            )

    @loader.command(
        ru_doc="- Включение/Выключение трансляции музыки в БИО", alias="биомуз"
    )
    async def togglestatus(self, message: Message):
        """Enable/disable music broadcasting in BIO"""
        if not self.config["api_key"] or not self.config["username"]:
            await utils.answer(message, self.strings["config_error"])
            await self.invoke("config", "BIOAudio", peer=message.peer_id)
            return

        self.audio_status = not self.audio_status
        self.set("audio_status", self.audio_status)
        status = (
            self.strings["enabled"] if self.audio_status else self.strings["disabled"]
        )

        if self.audio_status and not self.scrobbling_task:
            self.scrobbling_task = asyncio.create_task(self.scrobbling_loop())
        elif not self.audio_status and self.scrobbling_task:
            self.scrobbling_task.cancel()
            self.scrobbling_task = None

        await utils.answer(
            message, self.strings["status_changed"].format(status=status)
        )

    @loader.command(ru_doc="- Показать статистику прослушиваний", alias="музстат")
    async def lstats(self, message: Message):
        """Show listening statistics"""
        await utils.answer(message, self.strings["count_listened"])
        try:
            total = await self._request("user.getInfo", user=self.config["username"])
            week = await self._request(
                "user.getWeeklyTrackChart", user=self.config["username"]
            )
            month = await self._request(
                "user.getRecentTracks",
                user=self.config["username"],
                limit=1000,
                from_=int(time()) - 2592000,
            )

            total_tracks = total["user"]["playcount"]
            week_tracks = len(week["weeklytrackchart"]["track"])
            month_tracks = len(month["recenttracks"]["track"])

            await utils.answer(
                message,
                self.strings["stats"].format(
                    total=total_tracks, week=week_tracks, month=month_tracks
                ),
            )
        except Exception as e:
            await utils.answer(message, self.config["error_lstats"].format(e))
