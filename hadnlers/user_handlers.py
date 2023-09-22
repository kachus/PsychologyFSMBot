
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from services import save_info
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Filter
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    CallbackQuery
)
from keyboards.keyboard_ru import futher_or_back
from aiogram import Bot, F, Router, html

from aiogram.fsm.storage.memory import MemoryStorage
# import keyboards

router = Router()


class FSMQuestionForm(StatesGroup):
    fill_answer_problem = State()
    fill_emotions_state = State()
    fill_fear_reason_state = State()
    fill_worst_scenario = State()
    fill_desirable_emotion_state = State()
    fill_analysis_state = State()

@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    await state.set_state(FSMQuestionForm.fill_answer_problem)

    await message.answer('Привет! Этот бот поможет тебе разобраться'
                         'с проблемами! Опиши свою проблему в одном сообщении', reply_markup=futher_or_back)


@router.message(FSMQuestionForm.fill_answer_problem)
async def process_problem_command(message:Message, state: FSMContext):
    await state.set_state(FSMQuestionForm.fill_emotions_state)
    await save_info(message.from_user.id, 'emotions', message.text)
    await state.update_data(problem = message.text)
    await message.answer('Спасибо! А теперь опиши свои эмоции по этому поводу',
                         reply_markup=futher_or_back)


@router.message(FSMQuestionForm.fill_emotions_state)
async def process_emotion_command(message: Message, state: FSMContext):
    await state.update_data(emotions = message.text)
    await state.set_state(FSMQuestionForm.fill_fear_reason_state)
    await message.reply('Чего ты боищься в этой ситуации?')


@router.message(FSMQuestionForm.fill_fear_reason_state)
async def process_fear_reason(message: Message, state: FSMContext):
    await state.update_data(fear_reason = message.text)
    await state.set_state(FSMQuestionForm.fill_worst_scenario)
    await message.reply("Что самое ужасное может случиться с тобой в этой ситуации? "
                        "Опиши самый негативный исход")


@router.message(FSMQuestionForm.fill_worst_scenario)
async def process_fear_reason(message: Message, state: FSMContext):
    await state.update_data(worst_scenario = message.text)
    await state.set_state(FSMQuestionForm.fill_desirable_emotion_state)
    await message.reply("Опиши, какие эмоции ты бы хотел(а) испытывать в данной ситуации")


@router.message(FSMQuestionForm.fill_desirable_emotion_state)
async def process_fear_reason(message: Message, state: FSMContext):
    await state.update_data(desirable_emotions = message.text)
    await state.set_state(FSMQuestionForm.fill_analysis_state)
    await message.reply("А теперь немного подумай, такие ли большие последствия у твоих действий и так ли страшен исход?",
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=[
                            [
                                KeyboardButton(text = 'Да'),
                                KeyboardButton(text ='Нет')
                            ]
                        ], resize_keyboard=True,
                        ))

@router.message(FSMQuestionForm.fill_analysis_state, F.text.casefold()=="нет")
async def process_analysis(message: Message, state: FSMContext):
    await state.update_data(analysis= message.text)
    await state.clear()
    await message.reply("Спасибо!")


@router.message(FSMQuestionForm.fill_analysis_state, F.text.casefold()=="да")
async def process_analysis(message: Message, state: FSMContext):
    await state.update_data(analysis= message.text)
    await state.clear()
    await message.reply("Тогда перейдем к более глубокой практике, которая позволит"
                        "справиться со страхами")








# @router.message(FSMQuestionForm.fill_answer_problem)
# async def process_answer(message: Message, state : FSMContext):
#     await state.set_state(FSMQuestionForm.fill_answer_problem)
#     if message.text == "Дальше":
#         await state.set_state(FSMQuestionForm.fill_emotions_state)
#     else:
#         with open ('result.txt', 'a') as f:
#             f.write(message.text)
