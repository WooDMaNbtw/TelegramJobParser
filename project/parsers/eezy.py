import selenium.common
from databases.orm import ORM
from .base import ParserBase
import undetected_chromedriver
import time
from selenium.webdriver.common.by import By


class Eezy(ParserBase):

    def __init__(self, url='https://tyopaikat.eezy.fi/en'):
        super().__init__()
        self.url = url
        self.orm = ORM('databases/database.db')

    def accept_cookies(self, driver: undetected_chromedriver.Chrome):
        try:
            cookies = (driver
                .find_element(
                    By.CLASS_NAME,
                    'ch2-dialog-actions')
                .find_element(
                    By.CLASS_NAME,
                    'ch2-deny-all-btn')
            )
            cookies.click()
        except selenium.common.NoSuchElementException:
            pass

    def parse_by_selenium(self, title='', location=''):
        driver: undetected_chromedriver.Chrome = self.get_driver()

        driver.get(url=f"{self.url}?job={title}&location={location}")

        self.accept_cookies(driver=driver)

        content_block = driver.find_element(By.CLASS_NAME, 'css-1u0wjtf')

        while True:
            try:
                time.sleep(1)
                show_more = driver.find_element(By.CLASS_NAME, 'css-17kp6u6')
                show_more.click()
            except Exception as ex:
                break

        vacancies = content_block.find_elements(By.CLASS_NAME, 'css-7x9j97')

        for vacancy in vacancies:
            link = vacancy.find_element(By.TAG_NAME, 'a').get_attribute('href').replace('https://tyopaikat.eezy.fi', '')
            title = vacancy.find_element(By.CLASS_NAME, 'css-x9gms1').text
            industry = vacancy.find_element(By.CLASS_NAME, 'css-d0mjqo').text
            location = vacancy.find_element(By.CLASS_NAME, 'css-1o7vf0g').text

            self.orm.save_vacancy(
                table=Eezy.__name__,
                slug=link,
                title=title,
                description=industry,
                locations={"location": location}
            )
