from datetime import datetime

from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery

from BD.DBinterface import MongoDataBaseRepositoryInterface

from keyboards.callback_fabric import CategoryBeliefsCallbackFactory, CommonBeliefsCallbackFactory, \
    ExistingBeliefsCallbackFactory
from keyboards.inline_keyboards import create_define_way, \
    crete_category_keyboard_chose_belief_for_man, crete_keyboard_chose_belief_for_man, create_start_practice_kb, \
    crete_keyboard_chose_existing_belief_for_man

from aiogram import Bot, F, Router





router = Router()

#
# @router.callback_query(F.data == 'chose_old_beliefs')
# async def process_chose_belief(callback: CallbackQuery,
#                                callback_data: ExistingBeliefsCallbackFactory,
#                                bot: Bot,
#                                data_base):
#     keyboard = crete_keyboard_chose_existing_belief_for_man(user_telegram_id=callback.message.chat.id,
#                                                             data_base_controller=data_base)
#
#     await bot.edit_message_text(chat_id=callback.message.chat.id,
#                                 message_id=callback.message.message_id,
#                                 text=f"Выбери загон", reply_markup=keyboard)
