#Все хэндлеры с командами тут
#______________________________________________

from aiogram.filters import Command, CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from aiogram.types import Message

from BD.DBinterface import ClientRepository
from keyboards.keyboard_ru import futher_or_back
from aiogram import Bot, F, Router, html

#загрузка сценария шагов по сценарию "Определить убедждение"
from states.define_belif import FSMQuestionForm

router = Router()


@router.message(CommandStart())
# data_base: ClientRepository
async def command_start(message: Message, state: FSMContext, data_base: ClientRepository):
    await state.set_state(FSMQuestionForm.fill_answer_problem)
    await message.answer('Привет! Этот бот поможет тебе разобраться'
                         'с проблемами! Опиши свою проблему в одном сообщении', reply_markup=futher_or_back)