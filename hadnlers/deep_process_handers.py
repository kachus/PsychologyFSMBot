import datetime
import sys
import os
import time

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
from keyboards.inline_keyboards import create_futher_kb
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




class FSMQuestionForm(StatesGroup):
    prepare_state = State()
    remember_feeling_state = State()
    struggle_details = State()
    struggle_details_continue = State()
    emotions_state = State() #начало повторений
    emotions_state_enhance = State()
    body_feelings_state = State()
    body_feelings_enhance = State()
    emotion_visualization_state = State()
    question_root_state = State()
    find_root_state = State()
    proceed_emotion_root_state = State() #клавиатура с нескольими итерациями , рекурсивно
    destroy_emiton_state = State()
    root_event_details_state = State() # те же что и выше но на глубоком уровне
    child_figure_state = State()
    child_figure_continue_state = State()
    parent_figure_state = State()
    parent_figure_continue_state = State()
    dialogue_conclusion_state = State()
    peace_between_state = State()
    relaxation_state = State()
    new_deliefe_upper_state = State()
    new_belife_deeper_state = State()
    new_deliefe_upper_state_continue = State() #несколько повторений
    new_believe_formualtion_state = State()
    feedback_state = State()


@router.callback_query(F.data == 'start_belief')
async def start_practise(callback: CallbackQuery,
                                         bot: Bot,
                                         data_base,
                                         state: FSMContext):
    kb = create_futher_kb()
    await bot.send_message(chat_id=callback.from_user.id, text=LEXICON_RU['prepare_for_practice'],
                           reply_markup=kb)
    await state.set_state(FSMQuestionForm.prepare_state)


@router.callback_query(FSMQuestionForm.prepare_state,F.data == 'next_step')
async def relax_command(callback: CallbackQuery,
                                         bot: Bot,
                                         data_base,
                                         state: FSMContext):
    kb = create_futher_kb()
    for text in LEXICON_RU['instruction_relax']:
        await bot.send_message(chat_id=callback.from_user.id, text = text)
        time.sleep(5)
    await bot.send_message(chat_id=callback.from_user.id, text='Если ты чувствуешь расслабление, то нажми "К следующему шагу"', reply_markup=kb)
    # await bot.send_message(chat_id=callback.from_user.id, text=LEXICON_RU['instruction_relax'], reply_markup=kb)
    await state.set_state(FSMQuestionForm.remember_feeling_state)




@router.callback_query(FSMQuestionForm.remember_feeling_state, F.data == 'next_step')
async def remember_struggle_process(callback: CallbackQuery,
                                    bot: Bot,
                                    state: FSMContext,
                                    data_base,):
    kb = create_futher_kb()
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=LEXICON_RU['remember_struggle'], reply_markup=kb)
                                # reply_markup=keyboard)

    await state.set_state(FSMQuestionForm.struggle_details)



@router.message(FSMQuestionForm.struggle_details, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_adio_response(message: Message,
                                bot: Bot,
                                data_base,
                                state: FSMContext):
    await state.set_state(FSMQuestionForm.struggle_details)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.struggle_details, F.data == 'next_step')
async def process_next_step(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):
    await state.set_state(FSMQuestionForm.struggle_details_continue)
    # await bot.edit_message_text(chat_id=callback.message.chat.id,
    #                         message_id=callback.message.message_id,
    #                         text=LEXICON_RU['struggle_details']    )
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['struggle_details'],)









# @router.callback_query(F.data == 'start_belief')
# async def process_tell_beliefs_command(callback: CallbackQuery):
#     pass
