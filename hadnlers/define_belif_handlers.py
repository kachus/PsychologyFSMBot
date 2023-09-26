# Сценарий определения убеждения.
# ___________________________________________________________
import os

from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Filter
from pathlib import Path
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    CallbackQuery
)

from BD.DBinterface import ClientRepository
from BD.MongoDB.mongo_db import MongoClientUserRepositoryORM
from keyboards.keyboard_ru import futher_or_back
from aiogram import Bot, F, Router, html
from config_data.config import load_config
from aiogram.fsm.storage.memory import MemoryStorage

from services.save_info import save_user_info
from services.speech_processer import speech_to_voice_with_path
# загрузка сценария шагов по сценарию "Определить убедждение \ загон"
from states.define_belif import FSMQuestionForm

# import keyboards

router = Router()
config = load_config()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

# TODO: Сделать сценарий с выбор - Либо из списка готовых, либо свой.
# TODO: На каждом шаге сохранять ответ или в конце ? Выбор: сделать сохранения всех ответов в конце + вывод.


@router.message(FSMQuestionForm.start_define_believes, F.text.startswith('Поехали'))
async def start_define_believes_scenario(message: Message, state: FSMContext ):
    await state.set_state(FSMQuestionForm.fill_answer_problem)
    await message.answer('Теперь опиши проблему, с которой ты столкнулся.'
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



@router.message(FSMQuestionForm.fill_answer_problem, F.text.casefold()=='дальше')
async def process_problem_command(message: Message, state: FSMContext, data_base: ClientRepository):
    await state.set_state(FSMQuestionForm.fill_emotions_state)
    # save_user_info(message.from_user.id, 'emotions', message.text)
    await message.answer('Спасибо! А теперь опиши свои эмоции по этому поводу',
                         reply_markup=futher_or_back)


@router.message(FSMQuestionForm.fill_answer_problem)
async def process_problem_command(message: Message, state: FSMContext, data_base: ClientRepository):
    # if message.voice:
    #     file_id = message.voice.file_id
    #     file = await bot.get_file(file_id)
    #     file_path = file.file_path
    #     file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    #     await bot.download_file(file_path, destination=file_on_disk.as_posix())
    #     print(speech_to_voice_with_path(file_path=file_on_disk))

    with open('voice_data.txt', 'a') as problem_file:
        # problem = await state.get_data()
        problem_file.write(message.text)
    data = await state.update_data(emotions=message.text)
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
async def process_analysis(message: Message, state: FSMContext, data_base: ClientRepository):
    await state.update_data(analysis=message.text)
    await state.clear()
    await message.reply("Тогда перейдем к более глубокой практике, которая позволит"
                        "справиться со страхами")
