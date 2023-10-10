
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
from BD.MongoDB.mongo_db import MongoClientUserRepositoryORM
from BD.MongoDB.mongo_enteties import Answer
from aiogram.enums import ContentType
from aiogram import Bot, F, Router
from pathlib import Path
from services.speech_processer import speech_to_voice_with_path
from keyboards.inline_keyboards import create_futher_kb
from config_data.config import load_config
from services.services import save_answer

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
    emotions_state = State() #начало повторений
    emotions_state_enhance = State()
    body_feelings_state = State()
    body_feelings_enhance = State()
    emotion_visualization_state = State()
    question_root_state = State()
    find_root_state = State()
    proceed_emotion_root_state = State() #клавиатура с нескольими итерациями , рекурсивно
    destroy_emotion_state = State()
    root_event_details_state = State() # те же что и выше но на глубоком уровне
    root_event_contine = State()
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
    process_feedback_state = State()


@router.callback_query(F.data == 'start_belief')
async def start_practise(callback: CallbackQuery,
                                         bot: Bot,
                                         data_base,
                                         state: FSMContext):
    kb = create_futher_kb()
    await bot.send_message(chat_id=callback.from_user.id, text=LEXICON_RU['prepare_for_practice'],
                           reply_markup=kb)
    await state.set_state(FSMQuestionForm.prepare_state)


@router.callback_query(FSMQuestionForm.prepare_state, F.data == 'next_step')
async def relax_command(callback: CallbackQuery,
                                         bot: Bot,
                                         data_base,
                                         state: FSMContext):
    kb = create_futher_kb()
    for text in LEXICON_RU['instruction_relax']:
        await bot.send_message(chat_id=callback.from_user.id, text = text)

        # time.sleep(5)
    await bot.send_message(chat_id=callback.from_user.id, text='Если ты чувствуешь расслабление, то нажми "К следующему шагу"', reply_markup=kb)
    # await bot.send_message(chat_id=callback.from_user.id, text=LEXICON_RU['instruction_relax'], reply_markup=kb)
    await state.set_state(FSMQuestionForm.remember_feeling_state)


@router.callback_query(FSMQuestionForm.remember_feeling_state, F.data == 'next_step')
async def remember_struggle_process(callback: CallbackQuery,
                                    bot: Bot,
                                    state: FSMContext,
                                    data_base,):
    kb = create_futher_kb()
    await bot.send_message(chat_id=callback.message.chat.id,
                            text=LEXICON_RU['remember_struggle'], reply_markup=kb)
                                # reply_markup=keyboard)

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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    await state.set_state(FSMQuestionForm.struggle_details)
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.struggle_details, F.data == 'next_step')
async def process_next_step(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):

    await state.set_state(FSMQuestionForm.struggle_details_continue)
    kb = create_futher_kb()
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['struggle_details'], reply_markup=kb)


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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)



@router.callback_query(FSMQuestionForm.struggle_details_continue, F.data == 'next_step')
async def process_next_step(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.emotions_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['struggle_details_continue'],
                        reply_markup=kb)



@router.callback_query(FSMQuestionForm.emotions_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.body_feelings_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['enhance_emotions'],
                        reply_markup=kb)


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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)



@router.callback_query(FSMQuestionForm.body_feelings_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.emotion_visualization_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['body_response'],
                        reply_markup=kb)


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
    os.remove(path=file_on_disk)



@router.callback_query(FSMQuestionForm.emotion_visualization_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.question_root_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['root_struggle_question'],
                        reply_markup=kb)


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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.question_root_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.find_root_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['find_the_root_of_struggle'],
                        reply_markup=kb)


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
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.find_root_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.proceed_emotion_root_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['get_rid_of_emotion'],
                        reply_markup=kb)


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
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.proceed_emotion_root_state, F.data == 'next_step')
async def process_next_emotions(callback: CallbackQuery,
                            state: FSMContext,
                            bot: Bot,
                            data_base,):
    kb = create_futher_kb()
    await state.set_state(FSMQuestionForm.destroy_emotion_state)
    await bot.send_message(chat_id=callback.message.chat.id,
                        text=LEXICON_RU['find_reason'],
                        reply_markup=kb)


@router.callback_query(FSMQuestionForm.destroy_emotion_state, F.data == 'next_step')
async def process_query(callback: CallbackQuery,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):

    state.set_state(FSMQuestionForm.root_event_contine)
    kb = create_futher_kb()
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON_RU['deep_struggle_root'],
                           reply_markup=kb)

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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)


@router.callback_query(FSMQuestionForm.root_event_contine, F.data == 'next_step')
async def process_message(message:Message,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):
    state.set_state(FSMQuestionForm.child_figure_state)
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           reply_markup= kb,
                           text=LEXICON_RU['deep_sttruggle_situation'])

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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)


@router.message(FSMQuestionForm.child_figure_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)


@router.message(FSMQuestionForm.child_figure_state, F.data == 'next_step')
async def process_message(message:Message,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):
    state.set_state(FSMQuestionForm.child_figure_continue_state)
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['dialogue_adult_enhace_continue'])


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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)


@router.message(FSMQuestionForm.parent_figure_state, F.data == 'next_step')
async def process_message(message:Message,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):
    state.set_state(FSMQuestionForm.parent_figure_continue_state)
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['dialogue_to_kid'])



@router.message(FSMQuestionForm.parent_figure_continue_state, F.content_type.in_({ContentType.VOICE, ContentType.AUDIO}))
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
    print(speech_to_voice_with_path(file_path=file_on_disk))  # FIXME добавить апдейт в бд текст из аудио
    "update data in db"
    os.remove(path=file_on_disk)


@router.message(FSMQuestionForm.parent_figure_continue_state, F.data == 'next_step')
async def process_message(message:Message,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):
    state.set_state(FSMQuestionForm.dialogue_conclusion_state)
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['dialogue_to_adult_response'])


@router.message(FSMQuestionForm.dialogue_conclusion_state, F.data == 'next_step')
async def process_message(message:Message,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):
    state.set_state(FSMQuestionForm.peace_between_state)
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['dialogue_to_kid_response'])


@router.message(FSMQuestionForm.peace_between_state, F.data == 'next_step')
async def process_message(message:Message,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):
    state.set_state(FSMQuestionForm.relaxation_state)
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['peace_dialogue'])


@router.message(FSMQuestionForm.relaxation_state, F.data == 'next_step')
async def process_message(message:Message,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):
    state.set_state(FSMQuestionForm.new_believe_formualtion_state)
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['kid_adult_response'])


@router.message(FSMQuestionForm.new_believe_formualtion_state, F.data == 'next_step')
async def process_message(message:Message,
                        state: FSMContext,
                        bot: Bot,
                        data_base,):

    state.set_state(FSMQuestionForm.feedback_state)
    kb = create_futher_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['conclusion_practise'])


@router.message(FSMQuestionForm.feedback_state, F.data == 'next_step')
async def process_message(message: Message,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):

    state.set_state(FSMQuestionForm.process_feedback_state)
    kb = create_futher_kb() #FIXME добавить клавиатуру "завершить или оставить отзыв"
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU['Понравилась ли тебе практика? Ты можешь оставить свой отзыв или завершить ее'])


@router.message(FSMQuestionForm.feedback_state, F.data == 'next_step')
async def process_message(message: Message,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU[
                               'Спасибо за отзыв!'])


@router.message(FSMQuestionForm.feedback_state, F.data == 'finish_practice')
async def process_message(message: Message,
                          state: FSMContext,
                          bot: Bot,
                          data_base, ):
    await bot.send_message(chat_id=message.chat.id,
                           text=LEXICON_RU[
                               'Отличная работа! Поздравляю с завершением практики'])