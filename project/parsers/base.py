import abc
import os
import platform
import random
import undetected_chromedriver
from dotenv import load_dotenv
from selenium.webdriver import ChromeOptions
from typing import Optional
load_dotenv()


class ParserBase:

    def __init__(self):
        self.__proxy_login = os.environ.get('proxy_login')
        self.__proxy_password = os.environ.get('proxy_password')
        self.__agents_path = 'user-agents/user-agents.txt'
        if platform.system() == 'Windows':
            self.__driver_path = 'chromedrivers/windows/chromedriver'
        else:
            self.__driver_path = 'chromedrivers/linux/version_125/chromedriver'

    def __get_proxy(self) -> Optional[dict]:
        if not self.__proxy_login and not self.__proxy_password:
            return None

        proxy = f'https://{self.__proxy_login}:{self.__proxy_password}@46.232.15.69:8000'

        proxy_options = {
            'proxy': {
                'http': proxy,
                'https': proxy,
                'verify_ssl': False
            }
        }
        return proxy_options

    def __get_random_user_agent(self) -> str:
        with open(self.__agents_path, 'r') as file:
            user_agents = file.readlines()
            return random.choice(user_agents).strip()

    def get_driver(self) -> undetected_chromedriver.Chrome:
        options = ChromeOptions()
        options.add_argument("enable-automation")
        options.add_argument("--headless")
        options.add_argument("--window-size=1366,768")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-gpu")
        options.add_argument('--blink-settings=imagesEnabled=false')

        user_agent = self.__get_random_user_agent()
        options.add_argument(f"--user-agent={user_agent}")

        proxy = self.__get_proxy()
        driver = undetected_chromedriver.Chrome(
            driver_executable_path=self.__driver_path,
            options=options,
            # seleniumwire_options=proxy
        )

        return driver

    def get_description(self, driver: undetected_chromedriver.Chrome, link: str):
        pass





