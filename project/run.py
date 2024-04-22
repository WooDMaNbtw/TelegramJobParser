import datetime
import threading

from parsers.barona import Barona
from parsers.eezy import Eezy
from parsers.oikotie import Oikotie
from databases.orm import ORM


db = ORM('databases/database.db')


def parse_oikotie(keywords: list = '', location: str = '', is_remote: bool = False, industry: str = ''):
    oikotie = Oikotie()
    oikotie.parse_by_selenium(keywords=keywords, location=location, is_remote=is_remote, industry=industry)


def parse_eezy(title='', location=''):
    eezy = Eezy()
    eezy.parse_by_selenium(title=title, location=location)


def parse_barona(keyword=None, location=None):
    barona_parser = Barona()
    barona_parser.parse(keyword=keyword, location=location)


def main(oikotie_keywords='', oikotie_location='', oikotie_is_remote=False, oikotie_industry='',
         eezy_title='', eezy_location='',
         barona_keyword=None, barona_location=None):
    db.create_tables()

    start_time = datetime.datetime.now()

    # Создание и запуск потоков
    oikotie_thread = threading.Thread(target=parse_oikotie,
                                      args=(oikotie_keywords, oikotie_location, oikotie_is_remote, oikotie_industry))
    eezy_thread = threading.Thread(target=parse_eezy, args=(eezy_title, eezy_location))
    barona_thread = threading.Thread(target=parse_barona, args=(barona_keyword, barona_location))

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



