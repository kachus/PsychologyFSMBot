#Все хэндлеры с командами тут
#______________________________________________

from aiogram.filters import Command, CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from aiogram.types import Message

from BD.DBinterface import ClientRepository
from keyboards.keyboard_ru import futher_or_back, start_define_believes_kb
from aiogram import Bot, F, Router, html

#загрузка сценария шагов по сценарию "Определить убедждение"
from states.define_belif import FSMQuestionForm

router = Router()


@router.message(CommandStart())
# data_base: ClientRepository
async def command_start(message: Message, state: FSMContext, data_base: ClientRepository):
    await state.set_state(FSMQuestionForm.start_define_believes)
    await message.answer('Привет! Этот бот поможет тебе разобраться с твоими проблемами. Начнем?'
                         , reply_markup=start_define_believes_kb)