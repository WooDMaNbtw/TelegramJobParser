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

from telegram_bot import KanzuBot, Bot


async def runner() -> None:
    tasks = [
        # asyncio.create_task(KanzuBot.main_starter()),
        asyncio.create_task(Bot.main_starter()),
    ]

    await asyncio.gather(*tasks)

    commands = [
        BotCommand(command='/start', description='Menu'),
        BotCommand(command='/help', description='Help'),
        BotCommand(command='/info', description='info'),
        BotCommand(command='/settings', description='Settings'),
        # BotCommand(command='/select_vacancies', description='Настройки')
    ]
    await bot.set_my_commands(
        commands=commands
    )


if __name__ == '__main__':
    log_dir = os.path.join(f"{os.path.dirname(__file__)}/telegram_bot", 'TelegramLogs')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    file_handler = logging.FileHandler(os.path.join(log_dir, 'logs_tg.log'))
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(module)s - %(funcName)s  - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    try:
        asyncio.run(runner())
    except KeyboardInterrupt as ex:
        print("Error: ", ex)
