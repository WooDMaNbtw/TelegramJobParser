import os, asyncio, logging
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from assets import TG_API_BOT
from run import main

token: str = TG_API_BOT
bot = Bot(token=token)
dp = Dispatcher()

bot_design = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_education = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_engineering = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_finance = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_healthcare = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_it = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_legal = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_management = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_marketing = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_production = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_rad = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')
bot_sales = Bot(token='6795556806:AAGKyNG7T7BM1m42WGnqUZgyKvSzigugR0c')

from telegram_bot import (
    KanzuBot, DesignBot, EducationBot,
    EngineeringBot, FinanceBot, HealthcareBot,
    ITBot, LegalBot, ManagementBot, MarketingBot,
    ProductionBot, ResearchAndDevelopmentBot, SalesBot)


async def runner() -> None:
    tasks = [
        asyncio.create_task(KanzuBot.main_starter()),
        asyncio.create_task(DesignBot.main_starter()),
        asyncio.create_task(EducationBot.main_starter()),
        asyncio.create_task(EngineeringBot.main_starter()),
        asyncio.create_task(FinanceBot.main_starter()),
        asyncio.create_task(HealthcareBot.main_starter()),
        asyncio.create_task(ITBot.main_starter()),
        asyncio.create_task(LegalBot.main_starter()),
        asyncio.create_task(ManagementBot.main_starter()),
        asyncio.create_task(MarketingBot.main_starter()),
        asyncio.create_task(ProductionBot.main_starter()),
        asyncio.create_task(ResearchAndDevelopmentBot.main_starter()),
        asyncio.create_task(SalesBot.main_starter())
    ]

    await asyncio.gather(*tasks)

    commands = [
        BotCommand(command='/start', description='Начать'),
        BotCommand(command='/help', description='Помощь'),
        BotCommand(command='/settings', description='Настройки'),
        BotCommand(command='/select_vacancies', description='Настройки')
    ]
    await bot.set_my_commands(
        commands=commands
    )


if __name__ == '__main__':
    # log_dir = os.path.join(f"{os.path.dirname(__file__)}/telegram_bot", 'TelegramLogs')
    #
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)
    #
    # logging.basicConfig(level=logging.INFO)
    # logger = logging.getLogger()
    # file_handler = logging.FileHandler(os.path.join(log_dir, 'logs_tg.log'))
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(levelname)s - %(filename)s - %(module)s - %(funcName)s  - %(message)s')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    try:
        asyncio.run(runner())
    except KeyboardInterrupt as ex:
        print("Error: ", ex)
