from abc import ABC, abstractmethod

from BD.MongoDB.mongo_enteties import Client, Answer


class ClientRepository(ABC):
    """
    Интерфейс основан на MongoClientUserRepositoryORM
    поэтому использую дополнительно декоратор @staticmethod чтобы небыло конфликта
    """

    @staticmethod
    @abstractmethod
    def save_all_client_answers_by_id(user_telegram_id: int, answers: Answer) -> None:
        """
        Метод сохраняет все разговры клента
        """
        pass

    @staticmethod
    @abstractmethod
    def save_client_to_database(user: Client) -> None:
        """
        Метод сохраняет нового пользователя в базу данных
        Перед использованием нужно проверить пользвателя на наличие в базе данных по telegram id используя метод check_client_in_database
        Метод на вход принимает объект Client. Струкутру объекта смотреть в модуле mongo_enteties
        Поэтомк сначала необходимо инициализировать объект Client с полями:
            telegram_id = IntField(required=True)
            name = StringField()
            date_of_first_using = DateTimeField(required=True)
            date_of_last_visiting = DateTimeField()
            answers = ListField(ReferenceField(Answer))

            Где поле Answer это тектстовый ответ от пользоватея с полями
                    question = StringField()
                    scenario = StringField()
                    answer_date = DateTimeField
                    client_answer = StringField()
        :param user:
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def update_client_answer_by_chat_id(user_telegram_id: int, answer: dict) -> None:
        """
       Занести новые ответы в базу
        на вход принимает id telegramm пользователя и словарь  dict['названия_сценария'] = {
                'answer_date': datetime.now(),
        '       client_answers': ответ от пользоваетяля }
       :param user_telegram_id:
       :param answer:
       :return:
       """
        pass

    @staticmethod
    @abstractmethod
    def get_clients_answers_by_chat_id(user_telegram_id) -> list:
        pass

    @staticmethod
    @abstractmethod
    def retrieve_all_data_from_special_client_by_chat_id(user_telegram_id):
        pass

    @staticmethod
    @abstractmethod
    def check_client_in_database(user_telegram_id) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def retrieve_all_data_from_all_clients(self):
        pass


class ProblemsRepository(ABC):

    @abstractmethod
    def get_man_problems(self):
        pass

    @abstractmethod
    def get_woman_problems(self):
        pass


class MongoDataBaseRepositoryInterface(ABC):
    @abstractmethod
    def client_repository(self):
        pass

    @abstractmethod
    def problem_repository(self):
        pass
