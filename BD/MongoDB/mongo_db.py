from dataclasses import dataclass
from mongoengine import connect, DoesNotExist

from BD.MongoDB.mongo_enteties import Client
from config_data.config import load_config, Config


@dataclass
class MongoDB:
    bd_name: str
    host: str
    port: int

class MongoClientUserRepositoryORM:

    def __init__(self, mongo: MongoDB):
        connect(db=mongo.bd_name,
                host=mongo.host,
                port=mongo.port)

    @staticmethod
    def save_user_to_base(user: Client) -> None:
        user.save()
        print(f"пользователь c id: {Client.id}\nзанесен в базу \n {Client.objects}")

    @staticmethod
    def update_user_conversation_by_chat_id(user_telegram_id: int, answer: dict) -> None:
        user_to_update = Client.objects(telegram_id=user_telegram_id).get()
        user_to_update.conversation.append(answer)
        user_to_update.save()
        print(f"для пользователя c id: {user_telegram_id} \nответ: {answer}  \nзанесен в базу")

    @staticmethod
    def get_user_conversation_by_chat_id(user_telegram_id) -> list:
        user_answer = Client.objects(telegram_id=user_telegram_id).only("conversation").first()
        return user_answer.conversation

    @staticmethod
    def retrieve_all_data_from_special_user_by_chat_id(user_telegram_id):
        user_data = Client.objects(telegram_id=user_telegram_id).get()
        return user_data

    @staticmethod
    def check_user_in_database(user_telegram_id) -> bool:
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


    def retrieve_all_data_from_all_users(self):
        ...



if __name__ == '__main__':
    config: Config = load_config()
    configs = load_config()
    mongo_db = MongoDB(
        bd_name=configs.Data_base.bd_name,
        host=configs.Data_base.host,
        port=int(configs.Data_base.port),

    )

    #     cl_1 = Client(
    #     telegram_id = 123,
    #     name = 'джон',
    #     date_of_first_using = '01.02.2023',
    #     job = 'строитель',
    #     date_of_review = '01.02.2023',
    #     conversation = [
    #                        {"role": "assistent", "content": "ответ на бла бла бла "}
    #
    #                    ],
    # )

    user_repo = MongoClientUserRepositoryORM(mongo_db)
    # user_repo.save_answer(cl_1)

    conversation = {"role": "user", "content": "ЭТО АППЕНД"}
    print()
    # user_repo.save_answer(cl_1)
    # user_repo.update_user_answer_by_chatid(user_telegram_id=123, conversation=conversation)
    # data: Client = user_repo.retrieve_all_data_from_special_user_by_chatid(user_telegram_id=123)
    print()
    # print(data.conversation)
    # print(user_repo.check_user_in_database(user_telegram_id=12))

