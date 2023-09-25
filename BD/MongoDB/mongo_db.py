from dataclasses import dataclass

from environs import Env
from mongoengine import connect, DoesNotExist

from BD.DBinterface import ClientRepository, ProblemsRepository
from BD.MongoDB.mongo_enteties import Client, Answer, Problem
from config_data.config import load_config, Config, MongoDB


class MongoORMConnection:
    def __init__(self, mongo: MongoDB):
        connect(db=mongo.bd_name,
                host=mongo.host,
                port=mongo.port)


class MongoClientUserRepositoryORM(ClientRepository):

    @staticmethod
    def save_client_to_database(user: Client) -> None:
        user.save()
        print(f"пользователь c id: {Client.id}\nзанесен в базу \n {Client.objects}")

    @staticmethod
    def save_all_client_answers_by_id(user_telegram_id: int, answers:Answer) -> None:
        user_to_update = Client.objects(telegram_id=user_telegram_id).get()
        user_to_update.answers.append(answers)
        user_to_update.save()

    @staticmethod
    def update_client_answer_by_chat_id(user_telegram_id: int, answer: Answer) -> None:
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
        user_to_update = Client.objects(telegram_id=user_telegram_id).get()
        user_to_update.answers.append(answer)
        user_to_update.save()
        print(f"для пользователя c id: {user_telegram_id} \nответ: {answer}  \nзанесен в базу")

    @staticmethod
    def get_clients_answers_by_chat_id(user_telegram_id) -> list:
        """
        Получить ответы от определенного пользоватял по его telegram_id
        :param user_telegram_id:
        :return:
        """
        user_answer = Client.objects(telegram_id=user_telegram_id).only("conversation").first()
        return user_answer.conversation

    @staticmethod
    def retrieve_all_data_from_special_client_by_chat_id(user_telegram_id):
        """
        Ищвлекаем все имеющиеся данные с базы данных
        :param user_telegram_id:
        :return:
        """
        user_data = Client.objects(telegram_id=user_telegram_id).get()
        return user_data

    @staticmethod
    def check_client_in_database(user_telegram_id) -> bool:
        """
        проверяем пользователя в базе данных
        :return: bool
        """
        try:
            Client.objects(telegram_id=user_telegram_id).get()
            print(f"Пользователя с id: {user_telegram_id} \nесть в базе")
            return True
        except DoesNotExist:
            print(f"Пользователя с id: {user_telegram_id} \nне существует в базе данных")
            return False

    def retrieve_all_data_from_all_clients(self):
        ...


class MongoProblemsRepositoryORM(ProblemsRepository):
    def get_man_problems(self) -> list[Problem]:
        return Problem.objects(sex="man")

    def get_woman_problems(self) -> list[Problem]:
        return Problem.objects(sex="woman")


if __name__ == '__main__':
    env = Env()
    env.read_env()
    mongo_db = MongoDB(
        bd_name=env('DATABASE'),
        host=env('DB_HOST'),
        port=int(env('DB_PORT')),

    )
    MongoORMConnection(mongo_db)
    # user_repo = MongoClientUserRepositoryORM()
    # user_repo.save_answer(cl_1)

    print()
    # user_repo.save_answer(cl_1)
    # user_repo.update_user_answer_by_chatid(user_telegram_id=123, conversation=conversation)
    # data: Client = user_repo.retrieve_all_data_from_special_user_by_chatid(user_telegram_id=123)

    # print(data.conversation)
    # print(user_repo.check_user_in_database(user_telegram_id=12))
    a = MongoProblemsRepositoryORM().get_man_problems()
    b = MongoProblemsRepositoryORM().get_woman_problems()
    print()
