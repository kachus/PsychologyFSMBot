from aiogram.filters.callback_data import CallbackData


# TODO: Добавить название убежджения
class CommonBeliefsCallbackFactory(CallbackData, prefix='chose_common_beliefs'):
    belief_id: int
    category_id: str
    sex: str
    category_name_ru: str


class CategoryBeliefsCallbackFactory(CallbackData, prefix='category_common_beliefs'):
    category_id: str
    category_name_ru: str


class StartBeliefsFactory(CallbackData, prefix='start_belief'):
    belief_id: int
