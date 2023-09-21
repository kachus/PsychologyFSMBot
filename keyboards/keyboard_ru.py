from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from lexicon.lexicon_ru import LEXICON_RU


button_further: KeyboardButton= KeyboardButton(text = LEXICON_RU['further'], callback_data='next_step')
button_goback: KeyboardButton = KeyboardButton(text = LEXICON_RU['go_back'], callback_data='go_back')



basic_keyboard: ReplyKeyboardBuilder=ReplyKeyboardBuilder()
basic_keyboard.row(button_further, button_goback, width=2)

futher_or_back: ReplyKeyboardMarkup = basic_keyboard.as_markup(one_time_keyboard=True,
                                                               resize_keyboard=True)

