# Все хэндлеры с командами тут
# ______________________________________________
from datetime import datetime

from aiogram.filters import Command, CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from aiogram.types import Message

from BD.DBinterface import MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_enteties import Client
from keyboards.keyboard_ru import futher_or_back
from aiogram import Bot, F, Router, html

from services.services import save_user_if_not_exist
# загрузка сценария шагов по сценарию "Определить убедждение"
from states.define_belif import FSMQuestionForm

router = Router()


@router.message(CommandStart())
# data_base: ClientRepository
async def command_start(message: Message, state: FSMContext, data_base:MongoDataBaseRepositoryInterface):
    await state.set_state(FSMQuestionForm.fill_answer_problem)
    # Если пользователя нет в базе данных, то сохраняем в БД
    await save_user_if_not_exist(message, data_base)
    await message.answer('Привет! Этот бот поможет тебе разобраться'
                         'с проблемами! Опиши свою проблему в одном сообщении', reply_markup=futher_or_back)

