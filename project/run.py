import datetime
import threading

from parsers.barona import Barona
from parsers.eezy import Eezy
from parsers.oikotie import Oikotie
from databases.orm import ORM
import json
import undetected_chromedriver
from bs4 import BeautifulSoup
from selenium.webdriver import ChromeOptions
import time
from selenium.webdriver.common.by import By
import random

db = ORM('databases/database.db', )


def parse_oikotie():
    oikotie = Oikotie()
    oikotie.parse_by_selenium()


def parse_eezy():
    eezy = Eezy()
    eezy.parse_by_selenium()


def parse_barona():
    barona_parser = Barona()
    barona_parser.parse()


def main():
    start_time = datetime.datetime.now()

    # Создание и запуск потоков
    oikotie_thread = threading.Thread(target=parse_oikotie)
    eezy_thread = threading.Thread(target=parse_eezy)
    barona_thread = threading.Thread(target=parse_barona)

    oikotie_thread.start()
    eezy_thread.start()
    barona_thread.start()

    # Ожидание завершения потоков
    oikotie_thread.join()
    eezy_thread.join()
    barona_thread.join()

    end_time = datetime.datetime.now()

    print("Overall time: ", end_time - start_time)


if __name__ == "__main__":
    db.create_tables()
    main()



