from requests import get
from random import choice
from hikkatl.types import Message
from .. import loader, utils


@loader.tds
class AnekModule(loader.Module):
    """Модуль с анекдотами"""

    strings = {"name": "Anek"}

    @loader.command()
    async def anek(self, message: Message):
        """Получение рандомных шуток

        Какие типы шуток можно получить (использовать аргумент):
        1 - Анекдот
        2 - Рассказы
        3 - Стишки
        4 - Афоризмы
        5 - Цитаты
        6 - Тосты
        8 - Статусы
        11 - Анекдот (18+)
        12 - Рассказы (18+)
        13 - Стишки (18+)
        14 - Афоризмы (18+)
        15 - Цитаты (18+)
        16 - Тосты (18+)
        18 - Статусы (18+)"""

        URI = "http://rzhunemogu.ru/RandJSON.aspx?CType="
        anek_type = utils.get_args_raw(message)

        if anek_type and int(anek_type) in [
            1,2,3,4,5,6,8,11,12,13,14,15,18,
        ]:
            URI += anek_type
        else:
            URI += str(choice([1,2,3,4,5,6,8,11,12,13,14,15,18]))
        response = get(URI).text[12:-2]  # Проще обрезать. Это не JSON, это пиздец
        await utils.answer(message, response)
