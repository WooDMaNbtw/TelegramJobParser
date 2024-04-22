import json
from string import punctuation
from aiogram import Router, F, Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from runner import main

from runner import token

bot = Bot(token=token)
dp = Dispatcher()
router = Router()

SELECTED_OPTIONS = {
    'management': {
        'link': 'https://t.me/KanzuManagementBot',
        'message': "Management"
    },
    'it specialist': {
        'link': 'https://t.me/KaizenITBot',
        'message': "IT specialist"
    },
    'design': {
        'link': 'https://t.me/KaizenDesignBot',
        'message': "Design"
    },
    'marketing': {
        'link': 'https://t.me/KanzuMarketingBot',
        'message': "Marketing"
    },
    'finance': {
        'link': 'https://t.me/KanzuFinanceBot',
        'message': "Finance"
    },
    'production': {
        'link': 'https://t.me/KanzuProductionBot',
        'message': "Production"
    },
    'education': {
        'link': 'https://t.me/KanzuEducationBot',
        'message': "Education"
    },
    'healthcare': {
        'link': 'https://t.me/KanzuHealthcareBot',
        'message': "Healthcare"
    },
    'sales': {
        'link': 'https://t.me/KanzuSalesBot',
        'message': "Sales"
    },
    'engineering': {
        'link': 'https://t.me/KanzuEngineeringBot',
        'message': "Engineering"
    },
    'research and development': {
        'link': 'https://t.me/KanzuRnDBot',
        'message': "Research and Development"
    },
    'legal': {
        'link': 'https://t.me/KanzuLegalBot',
        'message': "Legal"
    }
}


@router.message(F.text.lower().startswith('job'))
async def select_vacancy_type(msg: Message) -> None:
    selected_type = msg.text.split(":")[1].lower()
    print(selected_type)
    data_from_selected_type = SELECTED_OPTIONS[selected_type]
    link = data_from_selected_type.get("link")
    message = data_from_selected_type.get("message")

    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="To vacancy", url=link))

    reply_message = (f"Please click a button below, you will be redirected "
                     f"to the chosen bot concerning *{selected_type.upper()}*")

    await msg.answer(
        text=reply_message,
        parse_mode='MarkdownV2',
        reply_markup=builder.as_markup()
    )


@router.message(Command('help'))
async def _help(msg: Message) -> None:

    await msg.answer(
        text='This is help block',
        parse_mode='MarkdownV2'
    )


@router.message(Command('select_vacancies'))
async def select_vacancies(msg: Message) -> None:

    await msg.answer(
        text='This is vacancies selection block',
        parse_mode='MarkdownV2'
    )

    types = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="job:Management")],
            [KeyboardButton(text="job:IT specialist")],
            [KeyboardButton(text="job:Design")],
            [KeyboardButton(text="job:Marketing")],
            [KeyboardButton(text="job:Finance")],
            [KeyboardButton(text="job:Production")],
            [KeyboardButton(text="job:Education")],
            [KeyboardButton(text="job:Healthcare")],
            [KeyboardButton(text="job:Sales")],
            [KeyboardButton(text="job:Engineering")],
            [KeyboardButton(text="job:Research and Development")],
            [KeyboardButton(text="job:Legal")],
        ],
        resize_keyboard=True,
    )

    await msg.answer(
        text="Please select wished types of vacancy.\n"
             "After selection you will be redirected to the chosen "
             "telegram bot of you trend.",
        reply_markup=types
    )


@router.message(Command('settings'))
async def settings(msg: Message) -> None:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Ru", callback_data='set_lang:rus'))
    builder.add(InlineKeyboardButton(text="En", callback_data='set_lang:eng'))
    builder.add(InlineKeyboardButton(text="Fi", callback_data='set_lang:fin'))

    await msg.answer(
        text='This is settings block',
        reply_markup=builder.as_markup(),
        parse_mode='MarkdownV2'
    )


@router.callback_query(F.data.startswith('set_lang'))
async def set_lang_rus(clb: CallbackQuery):
    lang_option = clb.data.split(':')[1]  # take chosen language
    await clb.message.answer(lang_option)
    file_lang_path: str = ''  # initialize var for filepath
    if lang_option == 'rus':
        file_lang_path = "/assets/rus/main.txt"

    elif lang_option == 'eng':
        file_lang_path = "assets/eng/main.txt"

    elif lang_option == 'fin':
        file_lang_path = "assets/fin/main.txt"

    with open(file_lang_path, "r") as file:
        dialogues = file.readlines()

    """

        Продумать

    """


@router.message(Command('start'))
async def start(msg: Message) -> None:

    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Отслеживать новые вакансии', callback_data=f"show_vacancies"))

    await msg.answer(
        text="*Ohayo, watashi wa Kaizen bot desu*",
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


@router.callback_query(F.data == 'show_vacancies')
async def show_vacancy(clb: CallbackQuery) -> Message:
    main()
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
        await clb.message.answer(
            parsed_message,
            parse_mode="MarkdownV2",
            reply_markup=builder.as_markup()
        )

    return await clb.message.answer(text="In a current time, thats all")


async def main_starter():

    dp.include_router(router)
    await dp.start_polling(bot)
