# Все хэндлеры с командами тут
# ______________________________________________
from datetime import datetime

from aiogram.filters import  CommandStart

from aiogram.fsm.context import FSMContext
from BD.MongoDB.mongo_enteties import Problem, Client

from aiogram.filters.state import State, StatesGroup
from BD.MongoDB.datat_enteties import Belief

from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile

from BD.DBinterface import MongoDataBaseRepositoryInterface

from keyboards.callback_fabric import CategoryBeliefsCallbackFactory, CommonBeliefsCallbackFactory
from keyboards.inline_keyboards import  \
    crete_category_keyboard_chose_belief_for_man, create_define_way,crete_keyboard_chose_belief_for_man, create_start_practice_kb, choose_gender_kb, crete_category_keyboard_chose_belief_for_woman, \
    create_keyboard_chose_belief, crete_category_keyboard


from aiogram import Bot, F, Router, html

from services.services import save_user_if_not_exist
# загрузка сценария шагов по сценарию "Определить убедждение"
from BD.MongoDB.mongo_enteties import Client

router = Router()


class FSMCommonCommands(StatesGroup):
    gender = State()
    female_category = State()
    male_category = State()
    female_struggle = State()
    male_struggle = State()


# #
# @router.message(CommandStart())
# async def command_start(message: Message,bot: Bot, state: FSMContext, data_base: MongoDataBaseRepositoryInterface):
#     # Если пользователя нет в базе данных, то сохраняем в БД
#     await save_user_if_not_exist(message, data_base)
#     #Клавиатура принимает id чата для того чтобы определить был он или нет в базе
#     inline_keyboard = create_define_way(database=data_base,
#                                         user_telegram_id=message.chat.id)
#     # await message.answer('Привет! Этот бот поможет разобраться тебе с твоими загонами!', reply_markup=inline_keyboard)
#     inline_keyboard = create_define_way(database=data_base,
#                                         user_telegram_id=message.chat.id)
#     await message.answer('Привет! Этот бот поможет разобраться тебе с твоими загонами!', reply_markup=inline_keyboard)
#
#     # Отправка анимации в сообщении



@router.message(CommandStart())
async def initial_keyboard(message: Message,bot: Bot, data_base: MongoDataBaseRepositoryInterface):
    await save_user_if_not_exist(message, data_base)
    #Клавиатура принимает id чата для того чтобы определить был он или нет в базе
    keyboard = choose_gender_kb()
    await bot.send_message(chat_id=message.chat.id,
                           text='Привет! Этот бот поможет разобраться тебе с твоими загонами! ⚡\nВыбери свой пол',
                           reply_markup=keyboard)


# @router.callback_query(F.data == 'initial')
# async def initial_keyboard(callback: CallbackQuery,bot: Bot, data_base: MongoDataBaseRepositoryInterface):
#
#     #Клавиатура принимает id чата для того чтобы определить был он или нет в базе
#     inline_keyboard = create_define_way(database=data_base,
#                                         user_telegram_id=callback.message.chat.id)
#     await bot.edit_message_text(chat_id=callback.message.chat.id,
#                                 message_id=callback.message.message_id,
#                                 text='Привет! Этот бот поможет разобраться тебе с твоими загонами!',
#                                 reply_markup=inline_keyboard)


@router.callback_query(F.data.contains('male'))
async def process_male_gender(callback: CallbackQuery, bot: Bot, data_base: MongoDataBaseRepositoryInterface,
                              state: FSMContext):
    inline_keyboard = create_define_way(database=data_base,
                                        user_telegram_id=callback.message.chat.id)
    if callback.data == 'female':
        data_base.client_repository.update_gender(user_id=callback.message.chat.id, gender='female')
    elif callback.data == 'male':
        data_base.client_repository.update_gender(user_id=callback.message.chat.id, gender='male')

    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text='Выбери подходящую команду',
                                reply_markup=inline_keyboard)


# @router.callback_query(F.data == 'male')
# async def process_male_gender(callback: CallbackQuery, bot: Bot, data_base: MongoDataBaseRepositoryInterface,
#                               state: FSMContext):
#     await state.update_data(gender='male')
#
#
#     inline_keyboard = create_define_way_male(database=data_base,
#                                         user_telegram_id=callback.message.chat.id)
#
#     data_base.client_repository.update_gender(user_id=callback.message.chat.id, gender='male')
#     await bot.edit_message_text(chat_id=callback.message.chat.id,
#                                 message_id=callback.message.message_id,
#                                 text='Выбери подходящую команду',
#                                 reply_markup=inline_keyboard)

@router.callback_query(F.data == 'chose_beliefs')
async def process_chose_beliefs_category(callback: CallbackQuery,
                                         bot: Bot,
                                         data_base,
                                         state: FSMContext):
    kb = crete_category_keyboard(user_id=callback.message.chat.id, data_base_controller = data_base)
    print('chosing category')

    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text="Выбери категорию",
                                reply_markup=kb)


@router.callback_query(F.data == 'tell_beliefs')
async def process_tell_beliefs_command(callback: CallbackQuery):
    ...

# @router.callback_query(F.data=='choose_beliefs')
# async def process_gender_choice(callback: CallbackQuery,
#                                 bot: Bot,
#                                 data_base):
#     kb = choose_gender_kb()
#     await bot.send_voice(chat_id=callback.message.id,
#                          )


@router.callback_query(CategoryBeliefsCallbackFactory.filter())
async def process_chose_belief(callback: CallbackQuery,
                               callback_data: CategoryBeliefsCallbackFactory,
                               bot: Bot,
                               data_base,):


    keyboard = create_keyboard_chose_belief(data_base_controller=data_base, user_id=callback.message.chat.id,
                                            category=callback_data.category_id,)
    #тут нужно отобразить категорию в коллбэе  полностью и не нужен пол
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=f"Категория: <b>{callback_data.category_name_ru}</b>"
                                     f"\n\nВыбери загон", reply_markup=keyboard)



# Если пользователь выбирает загон в этом сценарии то это новый загон
@router.callback_query(CommonBeliefsCallbackFactory.filter())
async def process_start_with_belief(callback: CallbackQuery,
                                    callback_data: CommonBeliefsCallbackFactory,
                                    bot: Bot,
                                    state: FSMContext,
                                    data_base):
    # получаем загон по его id
    print('belief_id:', callback_data.belief_id)
    print(callback_data.belief_id)
    belief = data_base.problem_repository.get_problem_by_problem_id(belief_id=callback_data.belief_id)
    await state.update_data(category=callback_data.category_name_ru)
    #Передаем в клавиатуру id загона
    keyboard = create_start_practice_kb(callback_data.belief_id)
    # сохраняем загон в базу данных для пользователя
    new_belief = Belief(
        belief=belief,
        first_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        last_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        dialogs=[]
    )
    data_base.client_repository.save_new_belief_to_user(user_telegram_id=callback.message.chat.id,
                                                        belief=new_belief.to_dict())# конвертация в словарь для записи в базу


    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f"Ты выбрал(а) загон: <b>{belief.belief}</b>"
                                f"\n\nНачнем работу?", reply_markup=keyboard)
    # TODO: Сделать передачу данных с ID загона
