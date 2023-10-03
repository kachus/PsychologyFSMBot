# Все хэндлеры с командами тут
# ______________________________________________
from datetime import datetime

from aiogram.filters import Command, CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from services.services import save_answer
from aiogram.types import Message, CallbackQuery

from BD.DBinterface import MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_enteties import Client
from keyboards.callback_fabric import CategoryBeliefsCallbackFactory, CommonBeliefsCallbackFactory
from keyboards.inline_keyboards import create_problem_chose_keyboard, create_define_way, \
    crete_category_keyboard_chose_belief_for_man, crete_keyboard_chose_belief_for_man, create_start_practice_kb
from keyboards.keyboard_ru import futher_or_back, start_define_believes_kb
from aiogram import Bot, F, Router, html

from services.services import save_user_if_not_exist
# загрузка сценария шагов по сценарию "Определить убедждение"
from states.define_belif import FSMQuestionForm

router = Router()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext, data_base: MongoDataBaseRepositoryInterface):
    # await state.set_state(FSMChoseScenario.enter_scenario)
    # Если пользователя нет в базе данных, то сохраняем в БД
    await save_user_if_not_exist(message, data_base)
    inline_keyboard = create_define_way()
    await message.answer('Привет! Этот бот поможет разобраться тебе с твоими загонами!', reply_markup=inline_keyboard)


# @router.message(FSMQuestionForm.enter_scenario, F.text.startswith('Поехали'))
# async def enter_define_belief_scenario(message:Message, state:FSMContext, data_base:MongoDataBaseRepositoryInterface):
#     # await state.set_state(FSMQuestionForm.start_define_believes)
#     await message.answer('Опиши свою проблему в одном сообщении', reply_markup=futher_or_back)
#     belief_kb = create_problem_chose_keyboard(data_base)
#     await state.set_state(FSMQuestionForm.start_define_believes)

@router.callback_query(F.data == 'tell_beliefs')
async def process_tell_beliefs_command(callback: CallbackQuery):
    ...


@router.callback_query(F.data == 'chose_beliefs')
async def process_chose_beliefs_category(callback: CallbackQuery,
                                         bot: Bot,
                                         data_base):
    keyboard = crete_category_keyboard_chose_belief_for_man(data_base)
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text="Выбери категорию",
                                reply_markup=keyboard)
    # await callback.message.answer("Выбери категорию", reply_markup=keyboard)


@router.callback_query(CategoryBeliefsCallbackFactory.filter())
async def process_chose_belief(callback: CallbackQuery,
                               callback_data: CategoryBeliefsCallbackFactory,
                               bot: Bot,
                               data_base):
    keyboard = crete_keyboard_chose_belief_for_man(category=callback_data.category_id,
                                                   data_base_controller=data_base)
    # await callback.message.answer()

    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=f"Категория: <b>{callback_data.category_name_ru}</b>"
                                     f"\n\nВыбери загон", reply_markup=keyboard)


@router.callback_query(CommonBeliefsCallbackFactory.filter())
async def process_start_with_belief(callback: CallbackQuery,
                                    callback_data: CommonBeliefsCallbackFactory,
                                    bot: Bot,
                                    state: FSMContext,
                                    data_base):
    await state.update_data(category=callback_data.category_name_ru)
    keyboard = create_start_practice_kb()
    #FIXME save category INTO DB
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f"Ты выбрал загон: <b>{callback_data.category_name_ru}</b>"
                                f"\n\nНачнем работу?", reply_markup=keyboard)



