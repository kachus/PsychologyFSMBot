from abc import ABC, abstractmethod

from BD.MongoDB.mongo_enteties import Client


class ClientRepository(ABC):
    """
    Интерфейс основан на MongoClientUserRepositoryORM
    поэтому использую дополнительно декоратор @staticmethod чтобы небыло конфликта
    """

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
    def update_client_answer_by_chat_id( user_telegram_id: int, answer: dict) -> None:
        """
       Занести новые ответы в базу
       на вход принимает id telegramm пользователя и объект Answer c с полями:
               question = StringField()
               scenario = StringField()
               answer_date = DateTimeField
               client_answer = StringField()
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