from databases.orm import ORM
from selenium.webdriver.common.by import By

from .base import ParserBase
import undetected_chromedriver
import time

from bs4 import BeautifulSoup


class Oikotie(ParserBase):

    def __init__(self):
        super().__init__()
        self.orm = ORM('databases/database.db')

    def parse_by_selenium(self, keyword: list = '', location: str = ''):

        driver: undetected_chromedriver.Chrome = self.get_driver()

        if location:
            location = '/' + location

        if keyword:
            keyword = f'&hakusana={",".join(keyword)}'

        url = (
           f'https://tyopaikat.oikotie.fi/tyopaikat/{location}?jarjestys=uusimmat{keyword}'
        )
        print(url)

        driver.get(url=url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        vacancies = soup.find_all('article', class_='job-ad-list-item')

        for vacancy in vacancies:
            body = vacancy.find('div', class_='body')

            title = body.find('h2').text.strip()
            slug = body.find('a').get('href')
            link = 'https://tyopaikat.oikotie.fi' + slug
            description = self.get_description(driver=driver, link=link)
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
                description=description,
                locations={'locations': location},
                employment_types={'employment_types': employment_types},
                posted_at=published
            )

    def get_description(self, driver: undetected_chromedriver.Chrome, link=str):
        driver.get(link)

        description = driver.find_element(By.CLASS_NAME, 'wysiwyg-container').text

        return description.strip()[:400] + "..."

