# Сценарий определения убеждения.
# ___________________________________________________________
import datetime
import sys
import os

from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Filter
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    CallbackQuery,
    InlineQuery
)

from BD.DBinterface import ClientRepository, MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_db import MongoClientUserRepositoryORM
from BD.MongoDB.mongo_enteties import Answer
from keyboards.keyboard_ru import futher_or_back
from aiogram.enums import ContentType
from aiogram import Bot, F, Router, html, Dispatcher
from pathlib import Path
from services.speech_processer import speech_to_voice_with_path

from config_data.config import load_config
from services.save_info import save_user_info
from services.services import save_answer
# загрузка сценария шагов по сценарию "Определить убедждение \ загон"
from states.define_belif import FSMQuestionForm
from lexicon.lexicon_ru import LEXICON_RU
# import keyboards
config = load_config()
bot = Bot(token=config.tg_bot.token)
# bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
router = Router()
new_data = {}


# TODO: Сделать сценарий с выбор - Либо из списка готовых, либо свой.


@router.callback_query(FSMQuestionForm.start_define_believes)
async def start_define_believes_scenario(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(FSMQuestionForm.fill_answer_problem)
    await bot.send_message(chat_id=callback_query.from_user.id, text='Теперь опиши проблему, с которой ты столкнулся.'
                         'Ты можешь написать несколько '
                         'сообщений. Нажми "Дальше", когда внесешь всю информацию и будешь готов перейти'
                         'к следующему шагу', reply_markup=futher_or_back)


@router.message(FSMQuestionForm.fill_answer_problem, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_voice_problem_command(message:Message, state: FSMContext):
    await state.set_state(FSMQuestionForm.fill_answer_problem)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=file_on_disk))
    "update data in db"
    os.remove(path=file_on_disk)

# Передал в качетсве пример data_base: ClientRepository в функцию под хэндлером
@router.message(FSMQuestionForm.fill_answer_problem, F.text==LEXICON_RU['further'])
async def process_problem_command(message: Message, state: FSMContext, data_base: ClientRepository):
    await state.set_state(FSMQuestionForm.fill_emotions_state)
    await state.update_data(problem=message.text) #FIXME сделать append записи
    await message.answer('Спасибо! А теперь опиши свои эмоции по этому поводу',
                         reply_markup=futher_or_back)


@router.message(FSMQuestionForm.fill_answer_problem)
async def process_problem_command(message: Message, state: FSMContext, data_base: ClientRepository):
    data = await state.update_data(emotions=message.text) #FIXME сделать append записи
    await state.set_state(FSMQuestionForm.fill_answer_problem)


@router.message(FSMQuestionForm.fill_emotions_state)
async def process_emotion_command(message: Message, state: FSMContext):
    await state.update_data(emotions=message.text)
    await state.set_state(FSMQuestionForm.fill_fear_reason_state)
    await message.reply('Чего ты боищься в этой ситуации?')


@router.message(FSMQuestionForm.fill_fear_reason_state)
async def process_fear_reason(message: Message, state: FSMContext):
    await state.update_data(fear_reason=message.text)
    await state.set_state(FSMQuestionForm.fill_worst_scenario)
    await message.reply("Что самое ужасное может случиться с тобой в этой ситуации? "
                        "Опиши самый негативный исход")


@router.message(FSMQuestionForm.fill_worst_scenario)
async def process_fear_reason(message: Message, state: FSMContext):
    await state.update_data(worst_scenario=message.text)
    await state.set_state(FSMQuestionForm.fill_desirable_emotion_state)
    await message.reply("Опиши, какие эмоции ты бы хотел(а) испытывать в данной ситуации")


@router.message(FSMQuestionForm.fill_desirable_emotion_state)
async def process_fear_reason(message: Message, state: FSMContext):
    await state.update_data(desirable_emotions=message.text)
    await state.set_state(FSMQuestionForm.fill_analysis_state)
    await message.reply(
        "А теперь немного подумай, такие ли большие последствия у твоих действий и так ли страшен исход?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Да'),
                    KeyboardButton(text='Нет')
                ]
            ], resize_keyboard=True,
        ))


# TODO: Подтверждение пользователем если нет выдаем что то типа: Давай еще раз, и запускаем сценарий опредеоления ограничивающего убеждения
@router.message(FSMQuestionForm.fill_analysis_state, F.text.casefold() == "нет")
async def process_analysis(message: Message, state: FSMContext):
    await state.update_data(analysis=message.text)
    await state.clear()
    await message.reply("Спасибо!")


# Конец сценария переходим к дркгому и сохранения ответов в базу данных
@router.message(FSMQuestionForm.fill_analysis_state, F.text.casefold() == "да")
async def process_analysis(message: Message, state: FSMContext, data_base: MongoDataBaseRepositoryInterface):
    await state.update_data(analysis=message.text)
    await save_answer(message=message,
                      data_to_save=await state.get_data(),
                      data_base=data_base
                      )

    await state.clear()
    await message.reply("Тогда перейдем к более глубокой практике, которая позволит"
                        "справиться со страхами")
