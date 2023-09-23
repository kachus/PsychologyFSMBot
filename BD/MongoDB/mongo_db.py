from dataclasses import dataclass

from environs import Env
from mongoengine import connect, DoesNotExist

from BD.MongoDB.mongo_enteties import Client
from config_data.config import load_config, Config


@dataclass
class MongoDB:
    bd_name: str
    host: str
    port: int


def save_client_to_database(user: Client) -> None:
    user.save()
    print(f"пользователь c id: {Client.id}\nзанесен в базу \n {Client.objects}")


class MongoClientUserRepositoryORM:

    def __init__(self, mongo: MongoDB):
        connect(db=mongo.bd_name,
                host=mongo.host,
                port=mongo.port)

    @staticmethod
    def update_client_answer_by_chat_id(user_telegram_id: int, answer: dict) -> None:
        user_to_update = Client.objects(telegram_id=user_telegram_id).get()
        user_to_update.conversation.append(answer)
        user_to_update.save()
        print(f"для пользователя c id: {user_telegram_id} \nответ: {answer}  \nзанесен в базу")

    @staticmethod
    def get_clients_answers_by_chat_id(user_telegram_id) -> list:
        user_answer = Client.objects(telegram_id=user_telegram_id).only("conversation").first()
        return user_answer.conversation

    @staticmethod
    def retrieve_all_data_from_special_client_by_chat_id(user_telegram_id):
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


if __name__ == '__main__':
    env = Env()
    env.read_env('.')
    mongo_db = MongoDB(
        bd_name=env('DeleteBelif'),
        host=env('localhost'),
        port=int(env('27017')),

    )

    user_repo = MongoClientUserRepositoryORM(mongo_db)
    # user_repo.save_answer(cl_1)


    print()
    # user_repo.save_answer(cl_1)
    # user_repo.update_user_answer_by_chatid(user_telegram_id=123, conversation=conversation)
    # data: Client = user_repo.retrieve_all_data_from_special_user_by_chatid(user_telegram_id=123)
    print()
    # print(data.conversation)
    # print(user_repo.check_user_in_database(user_telegram_id=12))
