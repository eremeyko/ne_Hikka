__version__ = (1, 8, 6)
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
from re import search

logger = logging.getLogger(f"LazyYT | {__version__}")


UPDATE_URL: str = "https://github.com/eremeyko/ne_Hikka/raw/master/LazyYouTube.py"


@loader.tds
class LazyYT(loader.Module):
    """Advanced YouTube Media Downloader using @Gozilla_bot"""

    strings = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>You has blocked the bot @Gozilla_bot!</b>\n"
            "Unblock the bot and try again later"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Please provide a valid YouTube link!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>This is not a valid YouTube link!</b>"
        ),
        "no_video": (
            "<emoji document_id=5219901967916084166>💥</emoji> <b>Unfortunately,"
            "it was not possible to get the video.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Unfortunately, "
            "it was not possible to get the audio.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Here\'s Your <a href="{link}">video:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Quality: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Author: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Here\'s Your <a href="{link}">audio:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Author: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Search your video...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Search your audio...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Downloading video</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Downloading audio</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> New version "
            "update available: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> To update, use: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Antispam!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "Try again in <code>{}</code> minutes or download another video"
        ),
        "_cmd_doc_yt": "[url] - Downloading video from YouTube",
        "_cmd_doc_ytm": "[url] - Downloading audio from YouTube",
    }

    strings_ru = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Вы заблокировали бота @Gozilla_bot!</b>\n"
            "Разблокируйте бота и повторите запрос ещё раз"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Пожалуйста, укажите ссылку на YouTube!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Это не ссылка на YouTube!</b>"
        ),
        "no_video": (
            "<emoji document_id=5219901967916084166>💥</emoji> "
            "<b>К сожалению, не удалось получить видео.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>К сожалению, не удалось получить аудио.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Вот Ваше <a href="{link}">видео:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Качество: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Автор: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Вот Ваше <a href="{link}">аудио:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Автор: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Идёт поиск видео...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Идёт поиск аудио...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Скачиваю видео</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Скачиваю аудио</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Доступно "
            "обновление до версии: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Для обновления "
            "используйте: <code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Сработала защита от спама!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "Это видео сейчас нельзя скачать.\n"
            "Попробуйте через {minutes} минут или скачайте другое видео"
        ),
        "_cmd_doc_yt": "[ссылка] - Скачивает видео из Ютуба",
        "_cmd_doc_ytm": "[ссылка] - Скачивает музыку из Ютуба",
    }

    # fork codrago only
    strings_uk = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Ви заблокували бота @Gozilla_bot!</b>\n"
            "Розблокуйте бота та спробуйте ще раз пізніше"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Будь ласка, надайте дійсне посилання на YouTube!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Це не дійсне посилання на YouTube!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>На жаль, не вдалося отримати відео.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>На жаль, не вдалося отримати аудіо.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Ось ваше <a href="{link}">відео:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Якість: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Автор: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Ось ваше <a href="{link}">аудіо:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Автор: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Шукаємо ваше відео...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Шукаємо ваше аудіо...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Завантажую відео</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Завантажую аудіо</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Доступне оновлення нової версії: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Для оновлення використовуйте: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Антиспам!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "Спробуйте ще раз через <code>{}</code> хвилин або завантажте інше відео"
        ),
        "_cmd_doc_yt": "[посилання] - Завантажує відео з YouTube",
        "_cmd_doc_ytm": "[посилання] - Завантажує аудіо з YouTube",
    }

    strings_fr = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Vous avez bloqué le bot @Gozilla_bot!</b>\n"
            "Débloquez le bot et réessayez plus tard"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Veuillez fournir un lien YouTube valide!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Ceci n'est pas un lien YouTube valide!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Malheureusement, il n'a pas été possible d'obtenir la vidéo.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Malheureusement, il n'a pas été possible d'obtenir l'audio.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Voici votre <a href="{link}">vidéo:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Qualité: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Auteur: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Voici votre <a href="{link}">audio:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Auteur: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Recherche de votre vidéo...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Recherche de votre audio...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Téléchargement de la vidéo</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Téléchargement de l'audio</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Nouvelle version disponible: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Pour mettre à jour, utilisez: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Antispam!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "Réessayez dans <code>{}</code> minutes ou téléchargez une autre vidéo"
        ),
        "_cmd_doc_yt": "[url] - Télécharge une vidéo depuis YouTube",
        "_cmd_doc_ytm": "[url] - Télécharge l'audio depuis YouTube",
    }

    strings_it = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Hai bloccato il bot @Gozilla_bot!</b>\n"
            "Sblocca il bot e riprova più tardi"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Per favore, fornisci un link YouTube valido!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Questo non è un link YouTube valido!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Purtroppo, non è stato possibile ottenere il video.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Purtroppo, non è stato possibile ottenere l'audio.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Ecco il tuo <a href="{link}">video:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Qualità: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Autore: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Ecco il tuo <a href="{link}">audio:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Autore: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Ricerca del tuo video...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Ricerca del tuo audio...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Download del video</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Download dell'audio</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Nuova versione disponibile: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Per aggiornare, usa: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Antispam!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "Riprova tra <code>{}</code> minuti o scarica un altro video"
        ),
        "_cmd_doc_yt": "[url] - Scarica video da YouTube",
        "_cmd_doc_ytm": "[url] - Scarica audio da YouTube",
    }

    strings_de = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Du hast den Bot @Gozilla_bot blockiert!</b>\n"
            "Entsperre den Bot und versuche es später erneut"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Bitte gib einen gültigen YouTube-Link an!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Dies ist kein gültiger YouTube-Link!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Leider konnte das Video nicht abgerufen werden.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Leider konnte das Audio nicht abgerufen werden.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Hier ist dein <a href="{link}">Video:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Qualität: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Autor: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Hier ist dein <a href="{link}">Audio:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Autor: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Suche nach deinem Video...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Suche nach deinem Audio...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Video wird heruntergeladen</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Audio wird heruntergeladen</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Neue Version verfügbar: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Zum Aktualisieren verwenden: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Antispam!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "Versuche es in <code>{}</code> Minuten erneut oder lade ein anderes Video herunter"
        ),
        "_cmd_doc_yt": "[url] - Lädt Video von YouTube herunter",
        "_cmd_doc_ytm": "[url] - Lädt Audio von YouTube herunter",
    }

    strings_tr = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Botu @Gozilla_bot engelledin!</b>\n"
            "Botu engel kaldır ve daha sonra tekrar dene"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Lütfen geçerli bir YouTube bağlantısı sağlayın!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Bu geçerli bir YouTube bağlantısı değil!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Maalesef video alınamadı.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Maalesef ses alınamadı.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>İşte <a href="{link}">videonuz:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Kalite: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Yazar: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>İşte <a href="{link}">sesiniz:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Yazar: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Videonuz aranıyor...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Sesiniz aranıyor...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Video indiriliyor</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Ses indiriliyor</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Yeni sürüm mevcut: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Güncellemek için kullanın: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Antispam!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "<code>{}</code> dakika sonra tekrar deneyin veya başka bir video indirin"
        ),
        "_cmd_doc_yt": "[url] - YouTube'dan video indirir",
        "_cmd_doc_ytm": "[url] - YouTube'dan ses indirir",
    }

    strings_uz = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Siz @Gozilla_bot botini blokladingiz!</b>\n"
            "Botni blokdan chiqaring va keyinroq qayta urinib ko'ring"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Iltimos, amal qiladigan YouTube havolasini taqdim eting!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Bu amal qiladigan YouTube havolasi emas!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Afsuski, video olish mumkin emas edi.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Afsuski, audio olish mumkin emas edi.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Manzilingizdagi <a href="{link}">video:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Sifat: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Muallif: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Manzilingizdagi <a href="{link}">audio:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Muallif: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Videoningiz qidirilmoqda...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Audiyangiz qidirilmoqda...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Video yuklanmoqda</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Audio yuklanmoqda</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Yangi versiya mavjud: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Yangilash uchun foydalaning: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Antispam!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "<code>{}</code> daqiqa ichida qayta urinib ko'ring yoki boshqa video yuklab oling"
        ),
        "_cmd_doc_yt": "[havola] - YouTube'dan video yuklash",
        "_cmd_doc_ytm": "[havola] - YouTube'dan audio yuklash",
    }

    strings_es = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>¡Has bloqueado el bot @Gozilla_bot!</b>\n"
            "Desbloquea el bot y vuelve a intentarlo más tarde"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>¡Por favor, proporciona un enlace de YouTube válido!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>¡Este no es un enlace de YouTube válido!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Lamentablemente, no se pudo obtener el video.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Lamentablemente, no se pudo obtener el audio.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Aquí está tu <a href="{link}">video:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Calidad: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Autor: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Aquí está tu <a href="{link}">audio:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Autor: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Buscando tu video...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Buscando tu audio...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Descargando video</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Descargando audio</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> ¡Nueva versión disponible: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Para actualizar, usa: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>¡Antispam!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "Vuelve a intentarlo en <code>{}</code> minutos o descarga otro video"
        ),
        "_cmd_doc_yt": "[url] - Descarga video de YouTube",
        "_cmd_doc_ytm": "[url] - Descarga audio de YouTube",
    }

    strings_kk = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Сіз @Gozilla_bot ботын бұғаттадыңыз!</b>\n"
            "Боты бұғаттан шығарыңыз және кейінірек қайта байқап көріңіз"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Жарамды YouTube сілтемесін көрсетіңіз!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Бұл жарамды YouTube сілтемесі емес!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Кешіріңіз, бейне алу мүмкін болмады.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Кешіріңіз, дыбыс алу мүмкін болмады.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Мына сіздің <a href="{link}">бейнеңіз:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Сапасы: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Авторы: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Мына сіздің <a href="{link}">дыбысыңыз:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Авторы: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Бейнеңіз ізделіп жатыр...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Дыбысыңыз ізделіп жатыр...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Бейне жүктелуде</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Аудио жүктелуде</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Жаңа нұсқа қолжетімді: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Жаңарту үшін пайдаланыңыз: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Антиспам!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "<code>{}</code> минуттан кейін қайта байқап көріңіз немесе басқа бейне жүктеп алыңыз"
        ),
        "_cmd_doc_yt": "[сілтеме] - YouTube-тен бейне жүктеу",
        "_cmd_doc_ytm": "[сілтеме] - YouTube-тен аудио жүктеу",
    }

    strings_tt = {
        "name": "LazyYouTube",
        "blocked_bot": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Сез @Gozilla_bot ботын блокладыгыз!</b>\n"
            "Ботны блоклардан чыгарыгыз һәм соңрак яңадан теләп карагыз"
        ),
        "no_link": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Зинһар, дөрес YouTube сылтамасын бирегез!</b>"
        ),
        "not_youtube": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Бу дөрес YouTube сылтамасы түгел!</b>"
        ),
        "no_video": (
            "<emoji document_id=5213460324425935151>❌</emoji> <b>Күзәтелә, видеоны алып булмый.</b>"
        ),
        "no_audio": (
            "<emoji document_id=5222472119295684375>🎶</emoji> <b>Күзәтелә, аудионы алып булмый.</b>"
        ),
        "your_video": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Монда сезнең <a href="{link}">видео:</b></a>\n'
            "{name}\n<emoji document_id=6019295596173596341>👁</emoji> <b>Сыйфат: </b>{quality} | "
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Автор: </b>{author}"
        ),
        "your_audio": (
            "<emoji document_id=5775981206319402773>🎞</emoji> "
            '<b>Монда сезнең <a href="{link}">аудио:</b></a>\n{name}\n'
            "<emoji document_id=5247213725080890199>📹</emoji> <b>Автор: </b>{author}"
        ),
        "searching_video": "<emoji document_id=5258274739041883702>🔍</emoji> Видео эзләнә...",
        "searching_audio": "<emoji document_id=5258274739041883702>🔍</emoji> Аудио эзләнә...",
        "downloading_video": "<emoji document_id=5213129047084584649>📥</emoji> <b>Видео йөкләнә</b> <code>{name}</code>...",
        "downloading_audio": "<emoji document_id=5213129047084584649>📥</emoji> <b>Аудио йөкләнә</b> <code>{name}</code>...",
        "update_available": (
            "\n\n<emoji document_id=5771695636411847302>📢</emoji> Яңа версия бар: {version}!\n<emoji "
            "document_id=5967816500415827773>💻</emoji> Яңарту өчен кулланыгыз: "
            "<code>.dlm {url}</code>"
        ),
        "antispam": (
            "<emoji document_id=5220197908342648622>❗️</emoji> <b>Антиспам!</b>\n"
            "<emoji document_id=5985616167740379273>⏰</emoji> "
            "<code>{}</code> минуттан соң яңадан теләп карагыз яки башка видеоны йөкләгез"
        ),
        "_cmd_doc_yt": "[сылтама] - YouTube'тан видео йөкләү",
        "_cmd_doc_ytm": "[сылтама] - YouTube'тан аудио йөкләү",
    }


    def __init__(self) -> None:
        """Инициализация. Прикол?"""
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "check_updates",
                True,
                lambda: "Check for updates on module load",
                validator=loader.validators.Boolean(),
            )
        )
        self.gozilla_bot = "@Gozilla_bot"
        self.gozilla_bot_id = 5229239434
        self.current_video_name = ""
        self.current_video_quality = ""
        self.current_video_author = ""
        self.current_url = ""
        self.update_message = ""

    def _is_youtube_url(self, url: str) -> bool:
        """Проверяет, является ли URL YouTube URL валидным
        
        Аргументы:
            url: Ютуб URL
            
        Возвращает:
            bool: True если URL является YouTube URL валидным, False в противном случае
        """
        youtube_patterns = [
            r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$',
            r'^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^(https?://)?(www\.)?youtu\.be/[\w-]+',
            r'^(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
        ]
        return any(search(pattern, url) for pattern in youtube_patterns)

    def _reset_media_info(self) -> None:
        """Сбрасывает информацию о текущем видео."""
        self.current_video_name = ""
        self.current_video_quality = ""
        self.current_video_author = ""

    @property
    def current_video_name(self) -> str:
        """Получает название текущего видео."""
        return self._current_video_name

    @current_video_name.setter
    def current_video_name(self, value: str) -> None:
        """Ставит название текущего видео."""
        self._current_video_name = value

    @property
    def current_video_quality(self) -> str:
        """Получает качество текущего видео."""
        return self._current_video_quality

    @current_video_quality.setter
    def current_video_quality(self, value: str) -> None:
        """Ставит качество текущего видео."""
        self._current_video_quality = value

    @property
    def current_video_author(self) -> str:
        """Получает автора текущего видео."""
        return self._current_video_author

    @current_video_author.setter
    def current_video_author(self, value: str) -> None:
        """Ставит автора текущего видео."""
        self._current_video_author = value

    @loader.loop(interval=10800, autostart=True, wait_before=False)
    async def check_for_updates(self) -> None:
        """Проверяет наличие обновлений каждые 3 часа."""
        try:
            logger.info("[LazyYouTube | Update Checker] Проверяю...")
            async with ClientSession() as session:
                async with session.get(UPDATE_URL) as response:
                    new_version_str = await response.text()
                    new_version_str = new_version_str.splitlines()[0].split("=")[1]
                    version_tuple = literal_eval(new_version_str)
                    if version_tuple > __version__:
                        self.update_message = self.strings["update_available"].format(
                            version=".".join(map(str, new_version_str)), url=UPDATE_URL
                        )
                        logger.info(
                            f"[LazyYouTube] New version available! {new_version_str} \n"
                            "Trying to update..."
                        )

                        await self.invoke("dlmod", UPDATE_URL, peer=self.logchat)
                    else:
                        self.update_message = ""
        except Exception as e:
            await logger.exception(f"Ошибка при проверке обновлений: {e}")

    async def client_ready(self, client: CustomTelegramClient, db: Database) -> None:
        """Инициализирует клиент и базу данных."""
        self.client: CustomTelegramClient = client
        self.gozilla_bot: TypeInputPeer = await self.client.get_entity(
            "Gozilla_bot"
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

    async def _find_by_url(self, name: str, mp3: bool = False, m: Optional[Message] = None) -> Optional[Message]:
        """Находит видео или аудио по URL.
        
        Аргументы:
            name: URL видео
            mp3: Если True, ищет аудио вместо видео
            m: Optional[Message] = None
            
        Возвращает:
            Optional[Message]: Сообщение с видео или аудио
            
        Ошибки:
            ValueError: Если замечен антиспам
            YouBlockedUserError: Если бот заблокирован
        """
        processing_message: Optional[Message] = None
        media_message: Optional[Message] = None
        antispam_minutes: Optional[str] = None
        button_clicked: bool = False
        processing_complete = asyncio.Event()
        self.current_url: str = name
        
        @self.client.on(events.NewMessage(from_users=self.gozilla_bot_id))
        async def get_quality_handler(event: events.NewMessage.Event) -> None:
            """Ловит сообщения от бота."""
            nonlocal processing_message, media_message, antispam_minutes, m, button_clicked
            try:
                if event.message.from_id == self.gozilla_bot_id:
                    # Проверка на антиспам
                    if "Antispam" in getattr(event.message, 'message', '') or "Antispam" in getattr(event, 'text', ''):
                        text = event.message.message if hasattr(event.message, 'message') else event.text
                        if match := search(r'(\d+)\s*minutes', text):
                            # Этот комментарий -- пасхалка :)
                            antispam_minutes = match.group(1)
                            try:
                                await utils.answer(
                                    m,
                                    self.strings("antispam").format(minutes=antispam_minutes) + self.update_message
                                )
                            except Exception as e:
                                logger.exception(f"[LazyYouTube] Error updating antispam message: {e}")
                            raise ValueError(f"antispam:{antispam_minutes}")
                        return

                    # Ловит сообщение с превью (содержит 👁)
                    if not button_clicked and event.message.photo and "👁" in event.message.text:
                        button_clicked = True  # От многократного нажатия
                        self._update_media_info(
                            name=event.message.text.split("\n")[0],
                            quality=event.message.reply_markup.rows[-2].buttons[0].text.split("-")[0][2:],
                            author=event.message.text.split("\n")[3][2:]
                        )
                        
                        # Сохраняем фото и обновляем сообщение
                        try:
                            
                            # Нажимаем на кнопку качества
                            await event.message.click((-2 if not mp3 else -1), 0)  # наоборот
                        except Exception as e:
                            logger.exception(f"[LazyYouTube] Error handling preview: {e}")
                            raise
                        return

                    # Ловит сообщение об обработке
                    if "👩‍🔬" in event.message.text:
                        await m.delete()
                        m = await utils.answer_file(
                            message=event.message,
                            file=event.message.photo,
                            caption=self.strings("downloading_" + ("audio" if mp3 else "video")).format(
                                name=self.current_video_name
                            )
                        )
                            
                        processing_message = event.message
                        return
                    
                    # Ловит сообщение с видео или аудио
                    if (mp3 and event.message.audio) or (not mp3 and event.message.video):
                        media_message = event.message
                        # Обновляем сообщение с фото на медиа
                        try:
                            await utils.answer_file(
                                message=m,
                                file=event.message.media,
                                caption=self.strings("your_" + ("audio" if mp3 else "video")).format(
                                    link=self.current_url,
                                    name=self.current_video_name,
                                    quality=self.current_video_quality if not mp3 else "",
                                    author=self.current_video_author,
                                ),
                                supports_streaming=True
                            )
                        except Exception as e:
                            logger.exception(f"[LazyYouTube] Error updating media message: {e}")
                            raise
                        finally:
                            processing_complete.set()
                        return
            except Exception as e:
                if isinstance(e, ValueError) and "antispam:" in str(e):
                    raise
                if not isinstance(e, MessageNotModifiedError):
                    logger.exception(f"[LazyYouTube] Error in quality handler:\n{e}")
                raise

        try:
            self.client.add_event_handler(get_quality_handler)
            
            # Отправляет URL в бота
            await self.client.send_message(self.gozilla_bot, name)
            await asyncio.sleep(0.5)
            
            try:
                await asyncio.wait_for(processing_complete.wait(), timeout=30)  # 30 секунд ожидания
            except asyncio.TimeoutError:
                logger.warning("[LazyYouTube] Processing timeout")
                return None
            
            return media_message
        finally:
            self.client.remove_event_handler(get_quality_handler)

    def _update_media_info(self, name: str, quality: str, author: str) -> None:
        """Обновляет информацию о текущем медиа.
        
        Args:
            name: Название медиа
            quality: Качество медиа
            author: Автор медиа
        """
        self.current_video_name = name
        self.current_video_quality = quality
        self.current_video_author = author

    @loader.command(alias="ют")
    async def yt(self, message: Message) -> None:
        """[url] - Downloading video from YouTube"""
        reply_to: Optional[Message] = await message.get_reply_message()
        
        if not (url := utils.get_args_raw(message)):
            if not reply_to or not (url := utils.get_args_raw(reply_to)):
                return await utils.answer(
                    message, self.strings("no_link") + self.update_message
                )
        
        if not self._is_youtube_url(url):
            return await utils.answer(
                message, self.strings("not_youtube") + self.update_message
            )

        try:
            m = await utils.answer(
                message, self.strings("searching_video") + self.update_message
            )
            
            if result := await self._find_by_url(name=url, mp3=False, m=m):
                await utils.answer_file(
                    message=m,
                    file=result,
                    supports_streaming=True,
                    caption=self.strings("your_video").format(
                        link=self.current_url,
                        name=self.current_video_name,
                        quality=self.current_video_quality,
                        author=self.current_video_author,
                    ),
                    reply_to=reply_to,
                )
                try:
                    await m.delete()
                except Exception as e:
                    logger.exception(f"[LazyYouTube] Error deleting message: {e}")
            else:
                await utils.answer(
                    message, self.strings("no_video") + self.update_message
                )

        except YouBlockedUserError:
            await utils.answer(message, self.strings["blocked_bot"] + self.update_message)
        except ValueError as e:
            if str(e).startswith("antispam:"):
                minutes = str(e).split(":")[1]
                await utils.answer(
                    message, 
                    self.strings("antispam").format(minutes=minutes) + self.update_message
                )
            else:
                logger.exception("[LazyYouTube] Unexpected ValueError in yt command")
                raise
        except Exception as e:
            logger.exception(f"[LazyYouTube] Error in yt command: {e}")
            raise

    @loader.command(alias="ютм")
    async def ytm(self, message: Message) -> None:
        """[url] - Downloading audio from YouTube"""
        reply_to: Optional[Message] = await message.get_reply_message()
        
        if not (url := utils.get_args_raw(message)):
            if not reply_to or not (url := utils.get_args_raw(reply_to)):
                return await utils.answer(
                    message, self.strings("no_link") + self.update_message
                )

        if not self._is_youtube_url(url):
            return await utils.answer(
                message, self.strings("not_youtube") + self.update_message
            )

        try:
            m = await utils.answer(
                message, self.strings("searching_audio") + self.update_message
            )

            if result := await self._find_by_url(name=url, mp3=True, m=m):
                await utils.answer_file(
                    message=m,
                    file=result,
                    supports_streaming=True,
                    caption=self.strings("your_audio").format(
                        link=self.current_url,
                        name=self.current_video_name,
                        author=self.current_video_author,
                    ),
                    reply_to=reply_to,
                )
                try:
                    await m.delete()
                except Exception as e:
                    logger.exception(f"[LazyYouTube] Error deleting message: {e}")
            else:
                await utils.answer(
                    message, self.strings("no_audio") + self.update_message
                )

        except YouBlockedUserError:
            await utils.answer(message, self.strings["blocked_bot"] + self.update_message)
        except ValueError as e:
            if str(e).startswith("antispam:"):
                minutes = str(e).split(":")[1]
                await utils.answer(
                    message, 
                    self.strings("antispam").format(minutes=minutes) + self.update_message
                )
            else:
                logger.exception("[LazyYouTube] Unexpected ValueError in ytm command")
                raise
        except Exception as e:
            logger.exception(f"[LazyYouTube] Error in ytm command: {e}")
            raise
