import datetime

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


def main():
    start_time = datetime.datetime.now()
    oikotie = Oikotie()
    oikotie.parse_by_selenium()
    eezy = Eezy()
    eezy.parse_by_selenium()
    barona_parser = Barona()
    barona_parser.parse()

    end_time = datetime.datetime.now()

    print("Overall time: ", end_time - start_time)


if __name__ == "__main__":
    db.create_tables()
    main()
