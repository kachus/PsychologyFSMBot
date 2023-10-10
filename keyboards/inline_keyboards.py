from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from environs import Env
from services.services import save_answer
from BD.DBinterface import MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_db import MongoORMConnection
from BD.MongoDB.mongo_enteties import Problem
from config_data.config import MongoDB
from container import data_base_controller
from keyboards.callback_fabric import CommonBeliefsCallbackFactory, CategoryBeliefsCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU

def create_start_practice_kb() -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    button = InlineKeyboardButton(text='Начать практику',
                                  callback_data='start_belief')
    kb_builder.row(button, width=1)
    return kb_builder.as_markup()


def create_problem_chose_keyboard(data_base_controller: MongoDataBaseRepositoryInterface) -> InlineKeyboardMarkup:
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    problems: list[Problem] = data_base_controller.problem_repository.get_man_problems()
    buttons = []
    for button in problems:
        buttons.append(InlineKeyboardButton(
            text=f'{str(button.problem).strip()[:30]}...',
            callback_data=str(button.problem).strip()[:30] #callback data can be changed
        ))

    kp_builder.row(*buttons, width=1)
    return kp_builder.as_markup()


def create_define_way() -> InlineKeyboardMarkup:
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    tell_beliefs = InlineKeyboardButton(text=f"{LEXICON_RU['tell_beliefs']}", callback_data='tell_beliefs')
    chose_beliefs = InlineKeyboardButton(text=f"{LEXICON_RU['chose_beliefs']}", callback_data='chose_beliefs')

    kp_builder.row(tell_beliefs, chose_beliefs, width=2)
    return kp_builder.as_markup()


def crete_category_keyboard_chose_belief_for_man(data_base_controller: MongoDataBaseRepositoryInterface):
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    problems: list[Problem] = data_base_controller.problem_repository.get_man_problems()
    find_categories = list(
        zip((category.category_id for category in problems), (category.category_ru for category in problems)))
    categories = []
    for category in find_categories:
        if category not in categories:
            categories.append(category)

    for category in categories:
        kp_builder.button(
            text=f'{category[1]}',
            callback_data=CategoryBeliefsCallbackFactory(
                category_id=category[0],
                category_name_ru=category[1]
            ).pack()
        )

    kp_builder.adjust(3)
    return kp_builder.as_markup()


def crete_keyboard_chose_belief_for_man(category: str, data_base_controller: MongoDataBaseRepositoryInterface): #FIXME добавление в коллбек поля belief из монго
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    problems: list[Problem] = data_base_controller.problem_repository.get_man_problems_by_category(
        category_name_id=category) #filtering data by received category
    for problem in problems:
        kp_builder.button(
            text=f'{str(problem.belief).strip()[:30]}...',
            callback_data=CommonBeliefsCallbackFactory(
                category_id=problem.category_id,
                sex=problem.sex,
                category_name_ru=problem.category_ru,
            ).pack()
        )
    kp_builder.button(
        text=f'< Назад категориям',
        callback_data="chose_beliefs"
    )
    kp_builder.adjust(1)
    return kp_builder.as_markup()


def create_futher_kb():
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    button_further: InlineKeyboardButton = InlineKeyboardButton(text = 'К следующему шагу', callback_data='next_step')
    kp_builder.row(button_further)
    return kp_builder.as_markup()

def leave_feedback_or_end_kb():
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    leave_fb_button: InlineKeyboardButton = InlineKeyboardButton(text = 'Оставить отзыв', callback_data='leave_feedback')
    finish_button: InlineKeyboardButton = InlineKeyboardButton(text='Закончить практику', callback_data='finish_practice')
    kb_builder.row(finish_button, leave_fb_button)
    return kb_builder.as_markup()