from aiogram.filters.callback_data import CallbackData

#TODO: Добавить название убежджения
class CommonBeliefsCallbackFactory(CallbackData, prefix='chose_common_beliefs'):
    category_id: str
    sex: str
    category_name_ru: str



class CategoryBeliefsCallbackFactory(CallbackData, prefix='category_common_beliefs'):
    category_id: str
    category_name_ru: str


