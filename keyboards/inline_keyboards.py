from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from BD.DBinterface import MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_enteties import Problem


def create_problem_chose_keyboard(data_base_controller:MongoDataBaseRepositoryInterface) -> InlineKeyboardMarkup:
    kp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    problems:list[Problem] = data_base_controller.problem_repository.get_man_problems()
    buttons =[]
    for button in problems:
        buttons.append(InlineKeyboardButton(
            text=f'{str(button.problem).strip()[:30]}...',
            callback_data=str(button.problem).strip()[:30]
        ))


    kp_builder.row(*buttons, width=1)
    return kp_builder.as_markup()