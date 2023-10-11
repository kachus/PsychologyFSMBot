from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from environs import Env
from services.services import save_answer
from BD.DBinterface import MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_db import MongoORMConnection, MongoClientUserRepositoryORM
from BD.MongoDB.mongo_enteties import Problem
from config_data.config import MongoDB
from container import data_base_controller
from keyboards.callback_fabric import CommonBeliefsCallbackFactory, CategoryBeliefsCallbackFactory, StartBeliefsFactory
from lexicon.lexicon_ru import LEXICON_RU


def create_start_practice_kb(belief_id) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    button = InlineKeyboardButton(text='Начать практику',
                                  callback_data=StartBeliefsFactory(
                                      belief_id=belief_id
                                  ).pack())
    kb_builder.row(button, width=1)
    return kb_builder.as_markup()


def create_problem_chose_keyboard(data_base_controller: MongoDataBaseRepositoryInterface) -> InlineKeyboardMarkup:
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    problems: list[Problem] = data_base_controller.problem_repository.get_man_problems()
    buttons = []
    for button in problems:
        buttons.append(InlineKeyboardButton(
            text=f'{str(button.belief).strip()[:30]}...',
            callback_data=str(button.belief).strip()[:30]  # callback data can be changed
        ))

    kp_builder.row(*buttons, width=1)
    return kp_builder.as_markup()


def create_define_way(database: MongoDataBaseRepositoryInterface, user_telegram_id: int) -> InlineKeyboardMarkup:
    """
    Функция создания клавиатуры для выбора пользователем действия
    Если пользоваетль уже работал над загоном то ему дается возможность выбрать статитсику и проработку своего загона
    """

    # клавиатура для ользователя который в первый раз
    def return_keyboard_for_new_user():
        kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        tell_beliefs = InlineKeyboardButton(text=f"{LEXICON_RU['tell_beliefs']}", callback_data='tell_beliefs')
        chose_beliefs = InlineKeyboardButton(text=f"{LEXICON_RU['chose_beliefs']}", callback_data='chose_beliefs')

        kp_builder.row(tell_beliefs, chose_beliefs, width=2)
        return kp_builder.as_markup()

    # клавиатура для ользователя который уже работал хотя бы над одним загоном ( Условие минимум 1 загон )
    def return_keyboard_for_existing_user():
        kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        tell_beliefs = InlineKeyboardButton(text=f"{LEXICON_RU['tell_beliefs']}", callback_data='tell_beliefs')
        chose_new_beliefs = InlineKeyboardButton(text=f"{LEXICON_RU['chose_beliefs']}", callback_data='chose_beliefs')
        chose_old_beliefs = InlineKeyboardButton(text=f"{LEXICON_RU['chose_old_beliefs']}",
                                                 callback_data='chose_old_beliefs')
        show_statistic = InlineKeyboardButton(text=f"{LEXICON_RU['show_statistic']}", callback_data='show_statistic')
        kp_builder.row(tell_beliefs, chose_new_beliefs, width=2)
        kp_builder.row(chose_old_beliefs, show_statistic, width=1)
        return kp_builder.as_markup()

    is_belief = database.client_repository.check_clients_belief_in_database(user_telegram_id)
    return return_keyboard_for_existing_user() if is_belief else return_keyboard_for_new_user()


def crete_category_keyboard_chose_belief_for_man(data_base_controller: MongoDataBaseRepositoryInterface):
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    problems: list[Problem] = data_base_controller.problem_repository.get_man_problems()
    find_categories = list(
        zip((category.category_id for category in problems), (category.category_ru for category in problems)))
    categories = []
    # Убираем дубликаты кактегорий
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


def crete_keyboard_chose_belief_for_man(category: str,
                                        data_base_controller: MongoDataBaseRepositoryInterface):  # FIXME добавление в коллбек поля belief из монго (ValueError: Resulted callback data is too long! len('chose_common_beliefs:11:Я не имею права отстаивать свою позицию.:girls:man:Девушки'.encode()) > 64)
    # Из за ограничения в 64 символа передаю только id загона. по этому id можно извлечь название из базы
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    problems: list[Problem] = data_base_controller.problem_repository.get_man_problems_by_category(
        category_name_id=category)  # filtering data by received category
    for problem in problems:
        kp_builder.button(
            text=f'{str(problem.belief).strip()[:30]}...',
            callback_data=CommonBeliefsCallbackFactory(
                belief_id=problem.belief_id,
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
    button_further: InlineKeyboardButton = InlineKeyboardButton(text='К следующему шагу', callback_data='next_step')
    kp_builder.row(button_further)
    return kp_builder.as_markup()
