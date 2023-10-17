import datetime
import os
import time

from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineQuery
)

from BD.DBinterface import ClientRepository, MongoDataBaseRepositoryInterface
from BD.MongoDB.datat_enteties import Belief, Dialog, DialogMessage, PassingPeriod
from BD.MongoDB.mongo_db import MongoClientUserRepositoryORM
from aiogram.enums import ContentType
from aiogram import Bot, F, Router
from pathlib import Path

from keyboards.callback_fabric import StartBeliefsFactory
from services.speech_processer import speech_to_voice_with_path
from keyboards.inline_keyboards import create_futher_kb
from config_data.config import load_config
from services.services import save_answer, add_dialog_data, get_data_to_save

# загрузка сценария шагов по сценарию "Определить убедждение \ загон"
from states.define_belif import FSMQuestionForm
from lexicon.lexicon_ru import LEXICON_RU

# import keyboards
config = load_config()
bot = Bot(token=config.tg_bot.token)

router = Router()
new_data = {}


class FSMQuestionForm(StatesGroup):
    prepare_state = State()
    remember_feeling_state = State()
    struggle_details = State()
    struggle_details_continue = State()
    emotions_state = State()  # начало повторений
    emotions_state_enhance = State()
    body_feelings_state = State()
    body_feelings_enhance = State()
    emotion_visualization_state = State()
    question_root_state = State()
    find_root_state = State()
    proceed_emotion_root_state = State()  # клавиатура с нескольими итерациями , рекурсивно
    destroy_emotion_state = State()
    root_event_details_state = State()  # те же что и выше но на глубоком уровне
    child_figure_state = State()
    child_figure_continue_state = State()
    parent_figure_state = State()
    parent_figure_continue_state = State()
    dialogue_conclusion_state = State()
    peace_between_state = State()
    relaxation_state = State()
    new_deliefe_upper_state = State()
    new_belife_deeper_state = State()
    new_deliefe_upper_state_continue = State()  # несколько повторений
    new_believe_formualtion_state = State()
    feedback_state = State()


# В этот сценарий приходит актульное убеждение которое пользователь выбрал на предыдщем шаге
# Предыдущий шаг может быть как новое убеждение так и проработка старого
# Данные которые должны приходить по убеждению 1. telegram id пользователя 2. id убеждения в базе
@router.callback_query(StartBeliefsFactory.filter())
async def start_practise(callback: CallbackQuery,
                         bot: Bot,
                         callback_data: StartBeliefsFactory,
                         data_base,
                         state: FSMContext):
    # Загружаем данные из по загону из базы по пользхователю и ID. В конце диалога ставим счетчик +1 для загона
    # belief: Belief = data_base.client_repository.get_user_belief_by_belief_id(user_telegram_id=callback.message.chat.id,
    #                                                                           belief_id=callback_data.belief_id)
    # belief.last_date = datetime.datetime.now()
    # замерям начальное время прохождения
    measure_time = PassingPeriod(
        start_time=datetime.datetime.now().time().strftime("%H:%M:%S")
    )

    dialog: Dialog = Dialog(
        conversation_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        messages=[],
        executed_time=measure_time
    )
    kb = create_futher_kb()
    dialog.messages.append(DialogMessage(
        number=len(dialog.messages) + 1,
        time=callback.message.date.time().strftime("%H:%M:%S"),
        bot_question=LEXICON_RU['prepare_for_practice'],
        step=str(state.get_state())
    ))
    await bot.send_message(chat_id=callback.from_user.id, text=LEXICON_RU['prepare_for_practice'],
                           reply_markup=kb)
    # await state.update_data(belief=belief, dialog=dialog)
    await state.update_data(dialog=dialog,belief_id=callback_data.belief_id)
    await state.set_state(FSMQuestionForm.prepare_state)


@router.callback_query(FSMQuestionForm.prepare_state, F.data == 'next_step')
async def relax_command(callback: CallbackQuery,
                        bot: Bot,
                        data_base,
                        state: FSMContext):
    print()
    kb = create_futher_kb()
    for text in LEXICON_RU['instruction_relax']:
        await bot.send_message(chat_id=callback.from_user.id, text=text)

        # time.sleep(5)
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Если ты чувствуешь расслабление, то нажми "К следующему шагу"', reply_markup=kb)
    # await bot.send_message(chat_id=callback.from_user.id, text=LEXICON_RU['instruction_relax'], reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date.time(),
                          bot_question=LEXICON_RU['instruction_relax'],
                          )
    await state.set_state(FSMQuestionForm.remember_feeling_state)


@router.callback_query(FSMQuestionForm.remember_feeling_state, F.data == 'next_step')
async def remember_struggle_process(callback: CallbackQuery,
                                    bot: Bot,
                                    state: FSMContext,
                                    data_base, ):
    kb = create_futher_kb()
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['remember_struggle'], reply_markup=kb)
    # reply_markup=keyboard)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['remember_struggle'],
                          )
    await state.set_state(FSMQuestionForm.struggle_details)


@router.message(FSMQuestionForm.struggle_details, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_audio_response(message: Message,
                                 bot: Bot,
                                 data_base,
                                 state: FSMContext):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    # FIXME добавить апдейт в бд текст из аудио.

    await add_dialog_data(state,
                          message_time=message.date,
                          bot_question=LEXICON_RU['remember_struggle'],
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix())
                          )

    await state.set_state(FSMQuestionForm.struggle_details)
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.struggle_details, F.data == 'next_step')
async def process_next_step(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base, ):
    await state.set_state(FSMQuestionForm.struggle_details_continue)
    kb = create_futher_kb()
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['struggle_details'], reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['struggle_details'],

                          )


@router.message(FSMQuestionForm.struggle_details_continue, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.struggle_details_continue)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())

    # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    # Добовляем в стейт данные
    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix())

                          )
    await state.set_state(FSMQuestionForm.struggle_details)
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.struggle_details_continue, F.data == 'next_step')
async def process_next_step(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base, ):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.emotions_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['struggle_details_continue'],
                           reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['struggle_details_continue']

                          )


@router.callback_query(FSMQuestionForm.emotions_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                                state: FSMContext,
                                bot: Bot,
                                data_base, ):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.body_feelings_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['enhance_emotions'],
                           reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['enhance_emotions']

                          )


@router.message(FSMQuestionForm.emotions_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.emotions_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())

    # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    # Добовляем в стейт
    await add_dialog_data(state,
                          message_time=message.date,
                          bot_question=LEXICON_RU['enhance_emotions'],
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )

    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.body_feelings_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                                state: FSMContext,
                                bot: Bot,
                                data_base, ):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.emotion_visualization_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['body_response'],
                           reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['body_response']

                          )


@router.message(FSMQuestionForm.body_feelings_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.body_feelings_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.emotion_visualization_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                                state: FSMContext,
                                bot: Bot,
                                data_base, ):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.question_root_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['root_struggle_question'],
                           reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['root_struggle_question']

                          )


@router.message(FSMQuestionForm.emotion_visualization_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.emotion_visualization_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=str(file_on_disk)))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.question_root_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                                state: FSMContext,
                                bot: Bot,
                                data_base, ):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.find_root_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['find_the_root_of_struggle'],
                           reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['find_the_root_of_struggle'],

                          )


@router.message(FSMQuestionForm.question_root_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.question_root_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.find_root_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                                state: FSMContext,
                                bot: Bot,
                                data_base, ):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.proceed_emotion_root_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['get_rid_of_emotion'],
                           reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['get_rid_of_emotion'],

                          )


@router.message(FSMQuestionForm.find_root_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.find_root_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.proceed_emotion_root_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                                state: FSMContext,
                                bot: Bot,
                                data_base, ):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.destroy_emotion_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['get_rid_of_emotion'],
                           reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU['get_rid_of_emotion'],

                          )

    #TODO: Вынести сохранение данных из стейта

    # data_to_save = await get_data_to_save(state)
    data = await state.get_data()
    dialog: Dialog = data.get('dialog')
    belief_id = data.get('belief_id')
    data_base.client_repository.save_belief_data(dialog=dialog,
                                                 user_telegram_id=callback.from_user.id,
                                                 belief_id=belief_id)






@router.message(FSMQuestionForm.destroy_emotion_state)
async def process_message(message: Message,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['find_reason'])

