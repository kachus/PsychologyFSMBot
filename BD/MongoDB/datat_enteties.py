# ________Классы для данных____________

from dataclasses import dataclass

from typing import List, Optional
from dataclasses import asdict

from BD.MongoDB.mongo_enteties import Problem


@dataclass
class PassingPeriod:
    """
    Класс данных для отметки начала и конца разговора.
    """

    start_time: Optional[str] = None
    end_time: Optional[str] = None


@dataclass
class DialogMessage:
    """
    Класс данных для хранения информации о конкретном сообщении.
    """
    number: int  # счетчик очередности сообщений в диалоге
    time: Optional[str] = None  # время сообщения в диалоге (понадобится для анализа)
    bot_question: Optional[str] = None
    user_answer: Optional[str] = None
    step: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Dialog:
    """
    Класс данных для хранения информации о полном диалоге.
    время
    """
    dialog_id:Optional[int]=None
    conversation_date: Optional[str] = None
    executed_time: Optional[PassingPeriod] = None
    messages: Optional[List[DialogMessage]] = None

    def to_dict(self):
        return asdict(self)
@dataclass
class Belief:
    """
    Класс данных для хранения информации о загоне.
    """
    belief: Optional[Problem] = None
    first_date: Optional[str] = None
    last_date: Optional[str] = None
    number_of_passages: int = 0  # Количество проработок
    dialogs: Optional[List[Dialog]] = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    # Конвертируем датакласс в словарь
    def to_dict(self):
        return asdict(self)


if __name__ == '__main__':
    a = Belief()
    print(a)
    print(a.to_dict())
