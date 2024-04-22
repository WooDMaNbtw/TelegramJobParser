import json
import os, asyncio, logging
from string import punctuation
from aiogram import Dispatcher, Bot, F
from aiogram.types import BotCommand
from typing import Any, Coroutine
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from runner import main
from bots_tokens import RAD_BOT_TOKEN


keywords = [
    "Research",
    "Development",
    "Innovation",
    "Scientific Research",
    "Product Development",
    "Experimental Design",
    "Data Analysis",
    "R&D Management",
    "Market Research",
    "Prototype Development",
    "Research Methodology",
    "Technology Development",
    "New Product Development",
    "Qualitative Research",
    "Quantitative Research",
    "Experimental Research",
    "Invention",
    "Patent",
    "Biotechnology",
    "Pharmaceutical Research"
]

bot = Bot(token=RAD_BOT_TOKEN)
dp = Dispatcher()
router = Router()


@router.message(Command('start'))
async def start(msg: Message) -> None:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Отслеживать новые вакансии', callback_data=f"show_vacancies::start"))

    await msg.answer(
        text="*Нажмите на кнопку для того чтобы начать отслеживать новые вакансии*",
        reply_markup=builder.as_markup(),
        parse_mode='MarkdownV2'
    )


async def reply_parse(replied_message: str) -> str:
    modified_text = ""
    for char in replied_message:
        if char in punctuation and char not in "`*_":
            modified_text += "\\" + char
        else:
            modified_text += char

    return modified_text


@router.callback_query(F.data.startswith('show_vacancies'))
async def show_vacancy(clb: CallbackQuery) -> Message:
    option = F.data.split("::")[1]
    while option == "start":

        main(oikotie_keywords=keywords[0], eezy_title=keywords[0], barona_keyword=keywords[0])
        with open("new_temp_vacancies.json", 'r') as file:
            vacancies: dict = json.load(fp=file)
        for slug, data in vacancies.items():
            '''
            data represents as a dictionary of key-values:

            service: name of the site (type - string)
            title: title of the vacancy (type - string)
            link: link to the vacancy (type - string)
            locations: a list of locations (type - string, represented - City, City..) 
            description: description of the vacancy (type - string)
            language: language of the vacancy (type - string, default - fi)
            '''

            builder = InlineKeyboardBuilder()

            builder.row(InlineKeyboardButton(text="To vacancy", url=data['link']))

            message = (f"*{data['title']}*\n"
                       f"|-🖥 Sourced: *{data['service']}*\n"
                       f"|-🗺 {data['locations']}\n"
                       f"|-🎙 language: {data['language'].upper()}\n"
                       f"`{data['description']}`")

            parsed_message = await reply_parse(message)
            return await clb.message.answer(
                parsed_message,
                parse_mode="MarkdownV2",
                reply_markup=builder.as_markup()
            )

        await asyncio.sleep(10)


async def main_starter():
    commands = [
        BotCommand(command='/start', description='Начать'),
        BotCommand(command='/help', description='Помощь'),
        BotCommand(command='/settings', description='Настройки'),
    ]

    await bot.set_my_commands(
        commands=commands
    )
    dp.include_router(router)
    await dp.start_polling(bot)

