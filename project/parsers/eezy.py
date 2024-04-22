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

    def parse_by_selenium(self, keyword='', location=''):
        driver: undetected_chromedriver.Chrome = self.get_driver()

        driver.get(url=f"{self.url}?job={keyword}&location={location}")

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
            try:
                link = vacancy.find_element(By.TAG_NAME, 'a').get_attribute('href')
                slug = link.replace('https://tyopaikat.eezy.fi', '')
            except Exception as ex:
                link = None
                slug = None

            title = vacancy.find_element(By.CLASS_NAME, 'css-x9gms1').text
            description = self.get_description(driver=driver, link=link)

            try:
                location = vacancy.find_element(By.CLASS_NAME, 'css-1o7vf0g').text
            except selenium.common.StaleElementReferenceException as ex:
                print("location wasn't found")

            self.orm.save_vacancy(
                table=Eezy.__name__,
                slug=slug,
                title=title,
                description=description,
                locations={"location": location}
            )

    def get_description(self, driver: undetected_chromedriver.Chrome, link=str):
        if link is None:
            return ''

        driver.get(link)

        description = driver.find_element(By.CLASS_NAME, 'css-4cffwv').text

        return description.strip()[:50] + "..."
