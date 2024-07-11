from requests import get
from json import loads
from re import sub
from hikkatl.types import Message
from .. import loader, utils


@loader.tds
class AnekModule(loader.Module):
    """Модуль с дедовскими анекдотами"""

    strings = {
        "name": "DedAnek"
    }

    @loader.command()
    async def anek(self, message: Message):
        """Получение рандомных шуток

Какие анекдоты можно получить (по умолчанию — 1):
1 - Анекдот
2 - Рассказы
3 - Стишки
4 - Афоризмы
5 - Цитаты
6 - Тосты
8 - Статусы
11 - Анекдот (+18)
12 - Рассказы (+18)
13 - Стишки (+18)
14 - Афоризмы (+18)
15 - Цитаты (+18)
16 - Тосты (+18)
18 - Статусы (+18)"""

        URI = "http://rzhunemogu.ru/RandJSON.aspx?CType="
        anek_type = utils.get_args_raw(message)

        if anek_type and int(anek_type) in [
            1,
            2,
            3,
            4,
            5,
            6,
            8,
            11,
            12,
            13,
            14,
            15,
            18,
        ]:
            URI += anek_type
        else:
            URI += "1"
        response = get(URI)
        data = loads(sub(r'[\x00-\x1F]+', 'epta', response.text))
        anekdot = data["content"].replace('epta', '\n') # костыли из-за кривого json на aspx
        await utils.answer(message, anekdot)
        return  # Предотвращает задвоение запроса
