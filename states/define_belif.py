from aiogram.filters.state import State, StatesGroup

class FSMQuestionForm(StatesGroup):
    start_define_believes = State()
    fill_answer_problem = State()
    fill_answer_problem_substate = State()
    fill_emotions_state = State()
    fill_fear_reason_state = State()
    fill_worst_scenario = State()
    fill_desirable_emotion_state = State()
    fill_analysis_state = State()

