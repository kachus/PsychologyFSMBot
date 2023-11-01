
from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery



from keyboards.callback_fabric import CategoryBeliefsCallbackFactory, CommonBeliefsCallbackFactory, \
    ExistingBeliefsCallbackFactory
from keyboards.inline_keyboards import  create_start_practice_kb, \
    crete_keyboard_chose_existing_belief_for_man

from aiogram import Bot, F, Router





router = Router()


@router.callback_query(F.data == 'chose_old_beliefs')
async def process_chose_existed_belief(callback: CallbackQuery,

                               bot: Bot,
                               data_base):
    keyboard = crete_keyboard_chose_existing_belief_for_man(user_telegram_id=callback.message.chat.id,
                                                            data_base_controller=data_base)

    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=f"Выбери загон", reply_markup=keyboard)


# Если пользователь выбирает загон в этом сценарии то это новый загон
@router.callback_query(ExistingBeliefsCallbackFactory.filter())
async def process_start_with_existed_belief(callback: CallbackQuery,
                                    callback_data: CommonBeliefsCallbackFactory,
                                    bot: Bot,
                                    state: FSMContext,
                                    data_base):
    # получаем загон по его id
    belief = data_base.problem_repository.get_problem_by_problem_id(callback_data.belief_id)
    await state.update_data(category=callback_data.category_name_ru)
    # Передаем в клавиатуру id загона
    keyboard = create_start_practice_kb(callback_data.belief_id)
    # сохраняем загон в базу данных для пользователя
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f"Ты выбрал загон: <b>{belief.belief}</b>"
                                f"\n\nНачнем работу?", reply_markup=keyboard)
