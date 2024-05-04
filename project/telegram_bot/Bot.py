import asyncio
import json
from string import punctuation
from typing import Union

import aiogram
from aiogram import Router, F, Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from runner import main, token
from run import db

bot = Bot(token=token)
dp = Dispatcher()
router = Router()
tracking_event = asyncio.Event()
tracking_event.clear()


@router.message(Command("start"))
@router.callback_query(F.data == "start")
async def start(msg: Union[Message, CallbackQuery]):
    """
    represents a start bot function
    :param msg: Message
    :return: Doesn't return any values
    """

    text = '''
ℹ️ Kanzu Navigation📌
    
Please select option in which you are interested
    '''

    parsed_text = await reply_parse(text)

    db.save_user(msg.from_user.id)

    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='To vacancies', callback_data=f"prepare_vacancies"))
    builder.row(InlineKeyboardButton(text='About service', callback_data='info'))
    builder.add(InlineKeyboardButton(text="Support", callback_data='help'))
    builder.row(InlineKeyboardButton(text='More our services', callback_data='services'))
    builder.add(InlineKeyboardButton(text='Settings', callback_data='settings'))

    answer_method = msg if isinstance(msg, Message) else msg.message

    await answer_method.delete()

    await answer_method.answer(
        text=parsed_text,
        reply_markup=builder.as_markup(),
        parse_mode="MarkdownV2"
    )


@router.callback_query(F.data == "prepare_vacancies")
async def prepare_vacancies(clb: CallbackQuery):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Start tracking vacancies")],
        ],
        resize_keyboard=True,
    )

    await clb.message.answer(
        text="Please submit the keyboard button to start tracking relevant vacancies",
        reply_markup=keyboard
    )


@router.message(F.text == "Start tracking vacancies")
@router.message(F.text == "Stop tracking vacancies")
async def vacancies(msg: Message):
    """
    Main method which requests the vacancies and responses to the user

    :param msg:
    :return: Doesn't return anything
    """

    ''' User option part '''
    global tracking_event
    if msg.text == "Start tracking vacancies":
        tracking_event.set()
    else:
        tracking_event.clear()

    option = tracking_event.is_set()

    if not option:
        await msg.answer(
            text="🛑 Tracking successfully stopped.",
        )
        return await start(msg=msg)

    ''' Informative part message '''
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Stop tracking vacancies")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    informative_message = await msg.answer(
        text='''
✅ Tracking started successfully, 

⚠️ Please be aware that vacancies won't be showed too often. 
The reason is that our service tracks vacancies from other websites and depends on them
    ''',
        reply_markup=keyboard
    )
    await informative_message.pin()

    while True:
        main()

        items_list: list = db.get_relevant_records(user_id=msg.from_user.id)

        items_list = items_list[-10:]

        for item in items_list:
            builder = InlineKeyboardBuilder()

            builder.row(InlineKeyboardButton(text="To vacancy", url=item[4]))
            message = (f"*{item[3]}*\n"
                       f"|-🗺 {item[5]}\n"
                       f"|-🎙 language: {item[9].upper()}\n"
                       f"`{item[7]}`")

            parsed_message = await reply_parse(message)
            await msg.answer(
                parsed_message,
                parse_mode="MarkdownV2",
                reply_markup=builder.as_markup(),
            )

            await asyncio.sleep(3)

        await asyncio.sleep(60 * 10)


@router.callback_query(F.data == "settings")
@router.message(Command("settings"))
async def settings(msg: Union[Message, CallbackQuery]):
    """
    Shows short description about language selection and 3 buttons:
    - Finland
    - English
    - Russian

    :return:
    """

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="To main menu", callback_data="start"))

    answer_method = msg if isinstance(msg, Message) else msg.message
    await answer_method.delete()
    await answer_method.answer(
        text="Settings",
        reply_markup=builder.as_markup(),
        parse_mode="MarkdownV2"
    )


@router.callback_query(F.data == "help")
@router.message(Command("help"))
async def help(msg: Union[Message, CallbackQuery]):
    """
    Shows short description about applying users issues or questions
    regarding our service.

    :return: It doesn't return any values, but texts to user such text:

    Text: example
    """

    text = '''
❓ Kanzu Support ❓

If you encountered any difficulties with our service, you can reach out to our managers via their Telegram profiles below:

1st manager: @SkyFyFamily
2nd manager: @woodmanbtw

⚠️ Please remember to be kind and observe the rules of decency while contacting our managers.

⚠️ Please note that due to a large number of requests, response times may take up to 24 hours.
    '''

    parsed_text = await reply_parse(text)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="To main menu", callback_data="start"))

    answer_method = msg if isinstance(msg, Message) else msg.message
    await answer_method.delete()
    await answer_method.answer(
        text=parsed_text,
        reply_markup=builder.as_markup(),
        parse_mode="MarkdownV2"
    )


@router.callback_query(F.data == "info")
@router.message(Command("info"))
async def info(msg: Union[Message, CallbackQuery]):
    """
    Shows info about current service and options which are used in.
    In addition, it should present how to use current service,
    for what purpose and to which benefits it leads

    :return: It doesn't return any values, but texts to user such text:
    """

    text = '''
ℹ️ About Our Service:

🔄 Every day, KanzuBot monitors numerous vacancies from the following websites:

- Barona
- Oikotie
- Eezy

Accordingly, it sends you relevant vacancies tailored to your skills and preferences.

✅ What Our Clients Receive:
A consistent monthly stream of hot leads actively searching for specialists like you.

    '''

    parsed_text = await reply_parse(text)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="To main menu", callback_data="start"))

    answer_method = msg if isinstance(msg, Message) else msg.message
    await answer_method.delete()
    await answer_method.answer(
        text=parsed_text,
        reply_markup=builder.as_markup(),
        parse_mode="MarkdownV2"
    )


async def main_starter():
    db.create_tables()
    dp.include_router(router)
    await dp.start_polling(bot)


async def reply_parse(replied_message: str) -> str:
    modified_text = ""
    for char in replied_message:
        if char in punctuation and char not in "`*_":
            modified_text += "\\" + char
        else:
            modified_text += char

    return modified_text
