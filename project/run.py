import asyncio
import datetime
import threading

from parsers.barona import Barona
from parsers.eezy import Eezy
from parsers.oikotie import Oikotie
from databases.orm import ORM


db = ORM('databases/database.db')


async def parse_oikotie(keyword: list = '', location: str = ''):
    oikotie = Oikotie()
    await oikotie.parse_by_selenium(keyword=keyword, location=location)


async def parse_eezy(keyword='', location=''):
    eezy = Eezy()
    await eezy.parse_by_bs4(keyword=keyword, location=location)


async def parse_barona(keyword=None, location=None):
    barona_parser = Barona()
    await barona_parser.parse(keyword=keyword, location=location)


async def main(keyword='', location=''):

    while True:
        start_time = datetime.datetime.now()

        await parse_barona()
        await parse_eezy()
        await parse_oikotie()

    # # Создание и запуск потоков
    # oikotie_thread = threading.Thread(target=parse_oikotie,
    #                                   args=(keyword, location))
    # eezy_thread = threading.Thread(target=parse_eezy, args=(keyword, location))
    # barona_thread = threading.Thread(target=parse_barona, args=(keyword, location))
    #
    # oikotie_thread.start()
    # eezy_thread.start()
    # barona_thread.start()
    #
    # # Ожидание завершения потоков
    # oikotie_thread.join()
    # eezy_thread.join()
    # barona_thread.join()

        end_time = datetime.datetime.now()

        print("Overall time: ", end_time - start_time)

        await asyncio.sleep(60 * 10)


if __name__ == "__main__":
    db.create_tables()
    main()



