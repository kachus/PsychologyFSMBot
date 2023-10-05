from datetime import datetime
from dataclasses import dataclass, asdict

from BD.MongoDB.mongo_enteties import Problem


from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from dataclasses import asdict

@dataclass
class PassingPeriod:
    """
    Класс данных для отметки начала и конца разговора.
    """
    conversation_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class DialogMessage:
    """
    Класс данных для хранения информации о конкретном сообщении.
    """
    number: int  # счетчик очередности сообщений в диалоге
    time: Optional[datetime] = None  # время сообщения в диалоге (понадобится для анализа)
    bot_question: Optional[str] = None
    user_answer: Optional[str] = None

@dataclass
class Dialogs:
    """
    Класс данных для хранения информации о полном диалоге.
    """
    executed_time: Optional[PassingPeriod] = None
    messages: Optional[List[DialogMessage]] = None

@dataclass
class Belief:
    """
    Класс данных для хранения информации о загоне.
    """
    belief: Optional[str] = None
    first_date: Optional[datetime] = None
    last_date: Optional[datetime] = None
    number_of_passages: int = 0  # Количество проработок
    dialogs: Optional[List[Dialogs]] = None

    # Конвертируем датакласс в словарь
    def to_dict(self):
        return asdict(self)


if __name__ == '__main__':
    a = Belief()
    print(a)
    print(a.to_dict())
