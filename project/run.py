import datetime
import threading

from parsers.barona import Barona
from parsers.eezy import Eezy
from parsers.oikotie import Oikotie
from databases.orm import ORM


db = ORM('databases/database.db')


def parse_oikotie(keyword: list = '', location: str = ''):
    oikotie = Oikotie()
    oikotie.parse_by_selenium(keyword=keyword, location=location)


def parse_eezy(keyword='', location=''):
    eezy = Eezy()
    eezy.parse_by_selenium(keyword=keyword, location=location)


def parse_barona(keyword=None, location=None):
    barona_parser = Barona()
    barona_parser.parse(keyword=keyword, location=location)


def main(keyword='', location=None):

    db.create_tables()

    start_time = datetime.datetime.now()

    # Создание и запуск потоков
    oikotie_thread = threading.Thread(target=parse_oikotie,
                                      args=(keyword, location))
    eezy_thread = threading.Thread(target=parse_eezy, args=(keyword, location))
    barona_thread = threading.Thread(target=parse_barona, args=(keyword, location))

    oikotie_thread.start()
    eezy_thread.start()
    barona_thread.start()

    # Ожидание завершения потоков
    oikotie_thread.join()
    eezy_thread.join()
    barona_thread.join()

    end_time = datetime.datetime.now()
    ORM.save_temp_vacancies()

    print("Overall time: ", end_time - start_time)


if __name__ == "__main__":
    db.create_tables()
    main()



