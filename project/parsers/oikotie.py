import requests
import dateutil.parser as date_parser
from databases.orm import ORM
from .base import ParserBase
import undetected_chromedriver
import time
from bs4 import BeautifulSoup


class Oikotie(ParserBase):

    def __init__(self):
        super().__init__()
        self.orm = ORM('databases/database.db')

    def parse_by_selenium(self, keywords: list = '', location: str = '', is_remote: bool = False, industry: str = ''):

        driver: undetected_chromedriver.Chrome = self.get_driver()

        if location:
            location = '/' + location

        if is_remote:
            remote_tag = '/etatyo'
        else:
            remote_tag = ''

        if industry:
            industry = f'&toimiala={industry}'

        if keywords:
            keywords = f'&hakusana={",".join(keywords)}'

        url = (
           f'https://tyopaikat.oikotie.fi/tyopaikat{location}{remote_tag}?jarjestys=uusimmat{keywords}{industry}'
               )

        driver.get(url=url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        vacancies = soup.find_all('article', class_='job-ad-list-item')

        for vacancy in vacancies:
            body = vacancy.find('div', class_='body')

            title = body.find('h2').text.strip()
            slug = body.find('a').get('href')
            company = body.find('span', class_='employer').text.strip()
            try:
                location = body.find('div', class_='locations').text.strip()
            except AttributeError as ex:
                location = None

            try:
                published = body.find('div', class_='publication-date').text.strip()
            except AttributeError as ex:
                published = None

            try:
                employment_types = body.find('div', class_='tag-list').text.replace('\n', '').replace(' ', '')
            except AttributeError as ex:
                employment_types = None

            self.orm.save_vacancy(
                table=Oikotie.__name__,
                title=title,
                slug=slug,
                description=company,
                locations={'locations': location},
                employment_types={'employment_types': employment_types},
                posted_at=published
            )


