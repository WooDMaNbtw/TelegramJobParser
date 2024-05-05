import asyncio
import json
from string import punctuation
from typing import Union
from aiogram import Router, F, Bot, Dispatcher
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


with open("telegram_bot/languages/langs.json", "r") as file:
    CUR_DICT_LANG: dict = json.load(fp=file)


@router.message(Command("start"))
@router.callback_query(F.data == "start")
async def start(msg: Union[Message, CallbackQuery]):
    global CUR_DICT_LANG
    db.save_user(msg.from_user.id)

    language: str = db.get_user_language(user_id=msg.from_user.id)

    """
    represents a start bot function which outputs buttons menu
    :param msg: Message
    :return: Doesn't return any values
    """

    text = CUR_DICT_LANG['start_menu_text'][language]

    parsed_text = await reply_parse(text)

    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(
        text=CUR_DICT_LANG['start_menu_buttons_text']['to_vacancies'][language],
        callback_data=f"prepare_vacancies")
    )
    builder.row(InlineKeyboardButton(
        text=CUR_DICT_LANG['start_menu_buttons_text']['about'][language],
        callback_data='info')
    )
    builder.add(InlineKeyboardButton(
        text=CUR_DICT_LANG['start_menu_buttons_text']['support'][language],
        callback_data='help')
    )
    builder.row(InlineKeyboardButton(
        text=CUR_DICT_LANG['start_menu_buttons_text']['more'][language],
        callback_data='services')
    )
    builder.add(InlineKeyboardButton(
        text=CUR_DICT_LANG['start_menu_buttons_text']['settings'][language],
        callback_data='settings'
    ))

    answer_method = msg if isinstance(msg, Message) else msg.message

    await answer_method.delete()

    await answer_method.answer(
        text=parsed_text,
        reply_markup=builder.as_markup(),
        parse_mode="MarkdownV2"
    )


@router.callback_query(F.data == "prepare_vacancies")
async def prepare_vacancies(clb: CallbackQuery):
    language: str = db.get_user_language(user_id=clb.from_user.id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CUR_DICT_LANG['vacancies_start_prepare_tracking_text'][language])],
        ],
        resize_keyboard=True,
    )

    await clb.message.answer(
        text=CUR_DICT_LANG['prepare_vacancies_text'][language],
        reply_markup=keyboard
    )


#  Current syntax is not clearly readable
@router.message(F.text == 'Start tracking vacancies')
@router.message(F.text == 'Начать отслеживание вакансий')
@router.message(F.text == 'Aloita työpaikkojen seuranta')
@router.message(F.text == 'Stop tracking vacancies')
@router.message(F.text == 'Прекратить отслеживание вакансий')
@router.message(F.text == 'Lopeta työpaikkojen seuranta')
async def vacancies(msg: Message):
    """
    Main method which requests the vacancies and responses to the user

    :param msg:
    :return: Doesn't return anything
    """
    language: str = db.get_user_language(user_id=msg.from_user.id)

    ''' User option part '''
    global tracking_event
    if msg.text == CUR_DICT_LANG['vacancies_start_prepare_tracking_text'][language]:
        tracking_event.set()
    else:
        tracking_event.clear()

    option = tracking_event.is_set()

    if not option:
        await msg.answer(
            text=CUR_DICT_LANG['vacancies_stopped_tracking_text'][language],
        )
        return await start(msg=msg)

    ''' Informative part message '''
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CUR_DICT_LANG['vacancies_stop_prepare_tracking_text'][language])],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    informative_message = await msg.answer(
        text=CUR_DICT_LANG['vacancies_started_tracking_text'][language],
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
    language: str = db.get_user_language(user_id=msg.from_user.id)

    text = CUR_DICT_LANG['settings_text'][language]

    parsed_text = await reply_parse(text)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Finnish', callback_data='set_finnish_lang'))
    builder.row(InlineKeyboardButton(text='English', callback_data='set_english_lang'))
    builder.row(InlineKeyboardButton(text='Русский', callback_data='set_russian_lang'))
    builder.row(InlineKeyboardButton(
        text=CUR_DICT_LANG['command_start_text'][language],
        callback_data="start")
    )

    answer_method = msg if isinstance(msg, Message) else msg.message
    await answer_method.delete()
    await answer_method.answer(
        text=parsed_text,
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
    language: str = db.get_user_language(user_id=msg.from_user.id)

    text = CUR_DICT_LANG['help_text'][language]

    parsed_text = await reply_parse(text)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=CUR_DICT_LANG['general_to_menu_text'][language], callback_data="start"))

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
    language: str = db.get_user_language(user_id=msg.from_user.id)

    text = CUR_DICT_LANG['info_text'][language]

    parsed_text = await reply_parse(text)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=CUR_DICT_LANG['general_to_menu_text'][language], callback_data="start"))

    answer_method = msg if isinstance(msg, Message) else msg.message
    await answer_method.delete()
    await answer_method.answer(
        text=parsed_text,
        reply_markup=builder.as_markup(),
        parse_mode="MarkdownV2"
    )


@router.callback_query(F.data == "set_russian_lang")
async def set_russian_lang(clb: CallbackQuery):
    db.set_user_language(user_id=clb.from_user.id, language='ru')
    return await start(msg=clb)


@router.callback_query(F.data == "set_english_lang")
async def set_english_lang(clb: CallbackQuery):
    db.set_user_language(user_id=clb.from_user.id, language='en')
    return await start(msg=clb)


@router.callback_query(F.data == "set_finnish_lang")
async def set_finnish_lang(clb: CallbackQuery):
    db.set_user_language(user_id=clb.from_user.id, language='fi')
    return await start(msg=clb)


async def main_starter():
    """
    Works as a main starter function

    :return: Doesn't return anything
    """
    db.create_tables()
    dp.include_router(router)
    await dp.start_polling(bot)


async def reply_parse(replied_message: str) -> str:
    """
    Modifies given text into parsed text, using \\

    :param replied_message:
    :return: modified text
    """
    modified_text = ""
    for char in replied_message:
        if char in punctuation and char not in "`*_":
            modified_text += "\\" + char
        else:
            modified_text += char

    return modified_text
