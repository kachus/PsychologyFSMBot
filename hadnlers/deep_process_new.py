import os
import time
import datetime
from asyncio import sleep
from typing import Any, Dict
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineQuery, FSInputFile
)

from keyboards.callback_fabric import StartBeliefsFactory

from BD.DBinterface import ClientRepository, MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_db import MongoClientUserRepositoryORM
from BD.MongoDB.datat_enteties import Belief, Dialog, DialogMessage, PassingPeriod
from aiogram.enums import ContentType
from aiogram import Bot, F, Router
from pathlib import Path

from services.services import save_answer, add_dialog_data, get_data_to_save, get_audio_duration
from services.speech_processer import speech_to_voice_with_path
from keyboards.inline_keyboards import create_futher_kb, leave_feedback_or_end_kb, create_define_way_male
from config_data.config import load_config
from services.services import save_answer

# загрузка сценария шагов по сценарию "Определить убедждение \ загон"
from states.define_belif import FSMQuestionForm
from lexicon.lexicon_ru import LEXICON_RU
from voice.match_key_file import get_file_path

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
    root_event_contine = State()
    child_figure_state = State()
    child_figure_continue_state = State()
    parent_figure_state = State()
    parent_figure_continue_state = State()
    dialogue_conclusion_state = State()
    peace_between_state = State()
    relaxation_state = State()
    new_beliefe_upper_state = State()
    new_belife_deeper_state = State()
    new_beliefe_upper_state_continue = State()  # несколько повторений
    new_believe_formualtion_state = State()
    process_final_emotions = State()
    feedback_state = State()
    process_feedback_state = State()


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

    #получаем пол пользователя
    data = await state.get_data()
    gender = data['gender']



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
        bot_question=LEXICON_RU.get(gender, 'key error').get('prepare_for_practice', 'key error'),
        # bot_question=LEXICON_RU.get(gender.get(['prepare_for_practice']),'key error'),
        step=str(await state.get_state())
    ))
    # await bot.send_message(chat_id=callback.from_user.id, text=LEXICON_RU.get(gender, 'key error').get('prepare_for_practice', 'key error'),
    #                        reply_markup=kb)
    # Отправляем голосовое

    await bot.send_voice(voice=FSInputFile(get_file_path('prepare_for_practice')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('prepare_for_practice', 'key error'),
                         # caption=LEXICON_RU.get(gender, 'key error').get('prepare_for_practice', 'key error'),
                         reply_markup=kb)

    await state.update_data(dialog=dialog, belief_id=callback_data.belief_id)
    await state.set_state(FSMQuestionForm.prepare_state)


@router.callback_query(FSMQuestionForm.prepare_state, F.data == 'next_step')
async def relax_command(callback: CallbackQuery,
                        bot: Bot,
                        data_base,
                        state: FSMContext):

    data = await state.get_data()
    gender = data['gender']

    kb = create_futher_kb()
    for num, text in enumerate(LEXICON_RU.get(gender, 'key error').get('instruction_relax', 'key error')):
        file_path = get_file_path(f'instruction_relax_{num}')
        await bot.send_voice(voice=FSInputFile(file_path), chat_id=callback.from_user.id,
                             caption=text,
                             )
        # ролучаем длинну аудиозаписи и сатвим на задержу по этой длине
        duration = await get_audio_duration(file_path)
        await sleep(duration)

    await bot.send_message(chat_id=callback.from_user.id,
                           text='Если ты чувствуешь расслабление, то нажми "К следующему шагу"', reply_markup=kb)
    # await bot.send_message(chat_id=callback.from_user.id, text=LEXICON_RU.get(gender, 'key error').get('instruction_relax', 'key error'), reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date.time(),
                          bot_question=LEXICON_RU.get(gender, 'key error').get('instruction_relax', 'kb key error'),
                          )  # TODO надо ли логировать инструкции?
    await state.set_state(FSMQuestionForm.remember_feeling_state)


@router.callback_query(FSMQuestionForm.remember_feeling_state, F.data == 'next_step')
async def remember_struggle_process(callback: CallbackQuery,
                                    bot: Bot,
                                    state: FSMContext,
                                    data_base, ):
    kb = create_futher_kb()
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('remember_struggle', 'key error'), reply_markup=kb)
    data = await state.get_data()
    gender = data['gender']

    await bot.send_voice(voice=FSInputFile(get_file_path('remember_struggle')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'kb error').get('remember_struggle', 'kb error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('remember_struggle', 'key error'),
                          )
    await state.set_state(FSMQuestionForm.struggle_details)


@router.message(FSMQuestionForm.struggle_details, F.content_type.in_({ContentType.VOICE}))
async def process_audio_response(message: Message,
                                 bot: Bot,
                                 data_base,
                                 state: FSMContext):
    data = await state.get_data()
    gender = data['gender']


    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    # FIXME добавить апдейт в бд текст из аудио. сейчас на каждый ответ своя запись?
    print(file_on_disk)
    await add_dialog_data(state,
                          message_time=message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('remember_struggle', 'key error'),
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

    data = await state.get_data()
    gender = data['gender']
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('struggle_details', 'key error'), reply_markup=kb)
    await bot.send_voice(voice=FSInputFile(get_file_path('struggle_details')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('struggle_details', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error',).get('struggle_details'),
                          )


@router.message(FSMQuestionForm.struggle_details_continue, F.content_type.in_({ContentType.VOICE}))
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
    data = await state.get_data()
    gender = data['gender']

    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.emotions_state)
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('struggle_details_continue', 'key error'),
    #                        reply_markup=kb)
    await bot.send_voice(voice=FSInputFile(get_file_path('struggle_details_continue')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('struggle_details_continue', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('struggle_details_continue', 'key error')
                          )


@router.callback_query(FSMQuestionForm.emotions_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                                state: FSMContext,
                                bot: Bot,
                                data_base, ):
    data = await state.get_data()
    gender = data['gender']

    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.body_feelings_state)
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('enhance_emotions', 'key error'),
    #                        reply_markup=kb)
    await bot.send_voice(voice=FSInputFile(get_file_path('enhance_emotions')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('enhance_emotions', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('enhance_emotions', 'key error')
                          )


@router.message(FSMQuestionForm.emotions_state, F.content_type.in_({ContentType.VOICE}))
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
    data = await state.get_data()
    gender = data['gender']

    # Добавляем в стейт
    print(file_on_disk.as_posix())
    await add_dialog_data(state,
                          message_time=message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('enhance_emotions', 'key error'),
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),
                          )
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.body_feelings_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                                state: FSMContext,
                                bot: Bot,
                                data_base, ):
    data = await state.get_data()
    gender = data['gender']

    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.emotion_visualization_state)
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('body_response', 'key error'),
    #                        reply_markup=kb)
    await bot.send_voice(voice=FSInputFile(get_file_path('body_response')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('body_response', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('body_response', 'key error')
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
    print(speech_to_voice_with_path(file_path=str(file_on_disk)))  # FIXME добавить апдейт в бд текст из аудио
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
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('root_struggle_question', 'key error'),
    #                        reply_markup=kb)
    data = await state.get_data()
    gender = data['gender']

    await bot.send_voice(voice=FSInputFile(get_file_path('root_struggle_question')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('root_struggle_question', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('root_struggle_question', 'key error')
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

    # FIXME добавить апдейт в бд текст из аудио
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
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('find_the_root_of_struggle', 'key error'),
    #                        reply_markup=kb)
    data = await state.get_data()
    gender = data['gender']

    await bot.send_voice(voice=FSInputFile(get_file_path('find_the_root_of_struggle')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('find_the_root_of_struggle', 'key error'),
                         reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('find_the_root_of_struggle', 'key error'),
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
    # FIXME добавить апдейт в бд текст из аудио

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
    data = await state.get_data()
    gender = data['gender']

    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.proceed_emotion_root_state)
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('get_rid_of_emotion', 'key error'),
    #                        reply_markup=kb)
    await bot.send_voice(voice=FSInputFile(get_file_path('get_rid_of_emotion')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('get_rid_of_emotion', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('get_rid_of_emotion', 'key error'),
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
    print(speech_to_voice_with_path(file_path=str(file_on_disk)))  # FIXME добавить апдейт в бд текст из аудио
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
    data = await state.get_data()
    gender = data['gender']


    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.destroy_emotion_state)
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('find_reason', 'key error'),
    #                        reply_markup=kb)
    await bot.send_voice(voice=FSInputFile(get_file_path('find_reason')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('find_reason', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('find_reason', 'key error'),
                          )


@router.callback_query(FSMQuestionForm.destroy_emotion_state, F.data == 'next_step')
async def process_query(callback: CallbackQuery,
                        state: FSMContext,
                        bot: Bot,
                        data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.root_event_contine)
    kb = create_futher_kb()
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        text=LEXICON_RU.get(gender, 'key error').get('deep_struggle_root', 'key error'),
    #                        reply_markup=kb)
    await bot.send_voice(voice=FSInputFile(get_file_path('deep_struggle_root')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('deep_struggle_root', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('deep_struggle_root', 'key error'),
                          )


@router.message(FSMQuestionForm.destroy_emotion_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.destroy_emotion_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    # FIXME добавить апдейт в бд текст из аудио

    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),
                          )

    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.root_event_contine, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.child_figure_state)
    kb = create_futher_kb()
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        reply_markup=kb,
    #                        text=LEXICON_RU.get(gender, 'key error').get('deep_sttruggle_situation', 'key error'))
    # fixme handler is not working
    await bot.send_voice(voice=FSInputFile(get_file_path('deep_sttruggle_situation')), chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('deep_sttruggle_situation', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('deep_sttruggle_situation', 'key error'),
                          )


@router.message(FSMQuestionForm.root_event_contine, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.root_event_contine)
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


@router.callback_query(FSMQuestionForm.child_figure_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.child_figure_state)
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


@router.callback_query(FSMQuestionForm.child_figure_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.child_figure_continue_state)
    kb = create_futher_kb()
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        reply_markup=kb,
    #                        text=LEXICON_RU.get(gender, 'key error').get('dialogue_adult_enhace_continue', 'key error'))
    await bot.send_voice(voice=FSInputFile(get_file_path('dialogue_adult_enhace_continue')),
                         chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('dialogue_adult_enhace_continue', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('dialogue_adult_enhace_continue', 'key error'),

                          )


@router.callback_query(FSMQuestionForm.child_figure_continue_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.parent_figure_continue_state)
    kb = create_futher_kb()
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        reply_markup=kb,
    #                        text=LEXICON_RU.get(gender, 'key error').get('dialogue_to_kid', 'key error'))
    await bot.send_voice(voice=FSInputFile(get_file_path('dialogue_to_kid')),
                         chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('dialogue_to_kid', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('dialogue_to_kid', 'key error'),

                          )


@router.message(FSMQuestionForm.child_figure_continue_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.child_figure_continue_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())

    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )
    os.remove(path=file_on_disk)


@router.message(FSMQuestionForm.parent_figure_continue_state,
                F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.parent_figure_continue_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=str(file_on_disk)))  # FIXME добавить апдейт в бд текст из аудио

    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.parent_figure_continue_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.dialogue_conclusion_state)
    kb = create_futher_kb()
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        reply_markup=kb,
    #                        text=LEXICON_RU.get(gender, 'key error').get('dialogue_to_adult_response', 'key error'))
    await bot.send_voice(voice=FSInputFile(get_file_path('dialogue_to_adult_response')),
                         chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('dialogue_to_adult_response', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('dialogue_to_adult_response', 'key error'),

                          )


@router.callback_query(FSMQuestionForm.dialogue_conclusion_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    await state.set_state(FSMQuestionForm.peace_between_state)
    kb = create_futher_kb()

    data = await state.get_data()
    gender = data['gender']

    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        reply_markup=kb,
    #                        text=LEXICON_RU.get(gender, 'key error').get('dialogue_to_kid_response', 'key error'))
    await bot.send_voice(voice=FSInputFile(get_file_path('dialogue_to_kid_response')),
                         chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('dialogue_to_kid_response', 'key error'),
                         reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('dialogue_to_kid_response', 'key error'),

                          )


@router.message(FSMQuestionForm.dialogue_conclusion_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.dialogue_conclusion_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())

    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.peace_between_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.relaxation_state)
    kb = create_futher_kb()
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        reply_markup=kb,
    #                        text=LEXICON_RU.get(gender, 'key error').get('peace_dialogue', 'key error'))
    await bot.send_voice(voice=FSInputFile(get_file_path('peace_dialogue')),
                         chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('peace_dialogue', 'key error'),
                         reply_markup=kb)
    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('peace_dialogue', 'key error'),
                          )


@router.message(FSMQuestionForm.peace_between_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.peace_between_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    # FIXME добавить апдейт в бд текст из аудио

    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                          )
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.relaxation_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.new_belife_deeper_state)
    kb = create_futher_kb()
    # await bot.send_message(chat_id=callback.message.chat.id,
    #                        reply_markup=kb,
    #                        text=LEXICON_RU.get(gender, 'key error').get('kid_adult_response', 'key error'))
    await bot.send_voice(voice=FSInputFile(get_file_path('kid_adult_response')),
                         chat_id=callback.from_user.id,
                         caption=LEXICON_RU.get(gender, 'key error').get('kid_adult_response', 'key error'),
                         reply_markup=kb)

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('kid_adult_response', 'key error'),
                          )


@router.message(FSMQuestionForm.new_belife_deeper_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.new_belife_deeper_state)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())

    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),
                          )

    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.new_belife_deeper_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.new_beliefe_upper_state)
    kb = create_futher_kb()
    try:
        await bot.send_voice(voice=FSInputFile(get_file_path('new_belief_upper_response_1')),
                             chat_id=callback.from_user.id,
                             caption=LEXICON_RU.get(gender, 'key error').get('new_belief_upper_response_1', 'key error'),
                             reply_markup=kb)
    except Exception as e:
        await bot.send_message(chat_id=callback.message.chat.id,
                               reply_markup=kb,
                               text=LEXICON_RU.get(gender, 'key error').get('new_belief_upper_response_1', 'key error'))

    await add_dialog_data(state,
                          message_time=callback.message.date,
                          bot_question=LEXICON_RU.get(gender, 'key error').get('new_belief_upper_response_1', 'key error'),

                          )


@router.message(FSMQuestionForm.new_beliefe_upper_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.new_beliefe_upper_state)
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


@router.callback_query(FSMQuestionForm.new_beliefe_upper_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    await state.set_state(FSMQuestionForm.new_beliefe_upper_state_continue)
    kb = create_futher_kb()

    data = await state.get_data()
    gender = data['gender']

    try:
        await bot.send_voice(voice=FSInputFile(get_file_path('new_belief_upper_response_2')),
                             chat_id=callback.from_user.id,
                             caption=LEXICON_RU.get(gender, 'key error').get('new_belief_upper_response_2', 'key error'),
                             reply_markup=kb)
    except Exception as e:
        await bot.send_message(chat_id=callback.message.chat.id,
                               reply_markup=kb,
                               text=LEXICON_RU.get(gender, 'key error').get('new_belief_upper_response_2', 'key error'))


@router.message(FSMQuestionForm.new_beliefe_upper_state_continue,
                F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.new_beliefe_upper_state_continue)
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    print(speech_to_voice_with_path(file_path=str(file_on_disk)))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"

    await add_dialog_data(state,
                          message_time=message.date,
                          user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix())
                          )

    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.new_beliefe_upper_state_continue, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    data = await state.get_data()
    gender = data['gender']

    await state.set_state(FSMQuestionForm.new_believe_formualtion_state)
    kb = create_futher_kb()
    try:
        await bot.send_voice(voice=FSInputFile(get_file_path('conclusion_practise')),
                             chat_id=callback.from_user.id,
                             caption=LEXICON_RU.get(gender, 'key error').get('conclusion_practise', 'key error'),
                             reply_markup=kb)
    except Exception as e:
        await bot.send_message(chat_id=callback.message.chat.id,
                               reply_markup=kb,
                               text=LEXICON_RU.get(gender, 'key error').get('conclusion_practise', 'key error'))


@router.message(FSMQuestionForm.new_believe_formualtion_state,
                F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
async def process_struggle_continue(message: Message,
                                    state: FSMContext,
                                    bot: Bot,
                                    data_base):
    await state.set_state(FSMQuestionForm.new_believe_formualtion_state)
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


@router.callback_query(FSMQuestionForm.new_believe_formualtion_state, F.data == 'next_step')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    await state.set_state(FSMQuestionForm.feedback_state)
    kb = leave_feedback_or_end_kb()
    await bot.send_message(chat_id=callback.message.chat.id,
                           reply_markup=kb,
                           text='Понравилась ли тебе практика? Ты можешь оставить свой отзыв или завершить ее')


@router.callback_query(FSMQuestionForm.feedback_state, F.data == 'leave_feedback')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    await state.set_state(FSMQuestionForm.process_feedback_state)
    # data = await state.get_data()
    # dialog: Dialog = data.get('dialog')
    # belief_id = data.get('belief_id')
    # data_base.client_repository.save_belief_data(dialog=dialog,
    #                                              user_telegram_id=callback.from_user.id,
    #                                              belief_id=belief_id)

    await bot.send_message(chat_id=callback.message.chat.id,
                           text='Можешь написать свой отзыв текстом тут или запись отзыв голосовым сообщением!')


@router.message(FSMQuestionForm.process_feedback_state)
async def process_message(message: Message,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    if F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}):
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
        await bot.download_file(file_path, destination=file_on_disk.as_posix())
        await add_dialog_data(state,
                              message_time=message.date,
                              bot_question='Отзыв',
                              user_answer=speech_to_voice_with_path(file_path=file_on_disk.as_posix()),

                              )
        os.remove(path=file_on_disk)
    else:
        await add_dialog_data(state,
                              message_time=message.date,
                              bot_question='Отзыв',
                              user_answer=message.text
                              )

    data = await state.get_data()
    dialog: Dialog = data.get('dialog')
    belief_id = data.get('belief_id')
    data_base.client_repository.save_belief_data(dialog=dialog,
                                                 user_telegram_id=message.from_user.id,
                                                 belief_id=belief_id)

    inline_keyboard = create_define_way_male(database=data_base,
                                        user_telegram_id=message.chat.id)
    await message.reply(text='Спасибо за отзыв!')
    await sleep(1)
    await bot.send_message(chat_id=message.chat.id,
                           text='Выбери что ты хочешь сделать',
                           reply_markup=inline_keyboard)


@router.callback_query(FSMQuestionForm.feedback_state, F.data == 'finish_practice')
async def process_message(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    inline_keyboard = create_define_way_male(database=data_base,
                                        user_telegram_id=callback.message.chat.id)
    data = await state.get_data()
    dialog: Dialog = data.get('dialog')
    belief_id = data.get('belief_id')
    data_base.client_repository.save_belief_data(dialog=dialog,
                                                 user_telegram_id=callback.from_user.id,
                                                 belief_id=belief_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text='Отличная работа! Поздравляю с завершением практики', reply_markup=inline_keyboard)
