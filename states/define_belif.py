from aiogram.filters.state import State, StatesGroup

class FSMQuestionForm(StatesGroup):
    fill_answer_problem = State()
    fill_emotions_state = State()
    fill_fear_reason_state = State()
    fill_worst_scenario = State()
    fill_desirable_emotion_state = State()
    fill_analysis_state = State()
