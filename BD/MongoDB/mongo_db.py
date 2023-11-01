from dataclasses import dataclass
from datetime import datetime

from aiogram.fsm.context import FSMContext
from environs import Env
from mongoengine import connect, DoesNotExist

from BD.DBinterface import ClientRepository, ProblemsRepository, MongoDataBaseRepositoryInterface
from BD.MongoDB.datat_enteties import Belief, Dialog
from BD.MongoDB.mongo_enteties import Client, Problem
from config_data.config import MongoDB


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

    @staticmethod #fixme
    def update_gender(user_id: int, gender: str) -> None:
        user_to_update = Client.objects(telegram_id=user_id).get()
        user_to_update.gender = gender
        user_to_update.save()
        print('сохранен пол:', gender)

    @staticmethod
    def get_user_gender(user_telegram_id: int) -> str:
        user = Client.objects(telegram_id=user_telegram_id).get()
        gender = user.gender
        print('пол того кто прорабатывает:', gender )
        return gender
    @staticmethod
    def save_all_client_answers_by_id(user_telegram_id: int, answers: dict) -> None:
        user_to_update = Client.objects(telegram_id=user_telegram_id).get()
        user_to_update.answers.append(answers)
        user_to_update.save()

    @staticmethod
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

    @staticmethod
    def check_clients_belief_in_database(user_telegram_id) -> bool:
        """
        проверяем есть ли у пользователя загон над котором он работал
        :return: bool
        """
        user = Client.objects(telegram_id=user_telegram_id).get()
        beliefs: list[dict] = user.beliefs
        return True if len(beliefs) > 0 else False

    @staticmethod
    def get_all_existing_beliefs_from_user_by_id(user_telegram_id) -> list:
        """
        Достаем все загоны над которыми работал пользователь
        :return: list
        """
        user = Client.objects(telegram_id=user_telegram_id).get()
        return user.beliefs

    @staticmethod
    def save_new_belief_to_user(user_telegram_id: int, belief: dict) -> None:
        """
        Фуция добавляет новый загон для пользоваителя по его id
        """
        user_to_save = Client.objects(telegram_id=user_telegram_id).get()
        user_to_save.beliefs.append(belief)
        try:
            user_to_save.save()
            print(f'Загон {belief}\nдля пользвателя {user_telegram_id}\nдобавлен')
        except Exception as e:
            print("что то пошло не так при сохранении нового загона в базу", e.message, e.args, )

    @staticmethod
    def get_user_belief_by_belief_id(user_telegram_id: int, belief_id: dict) -> Belief:
        user = Client.objects(telegram_id=user_telegram_id).get()
        user_beliefs = user.beliefs
        user_belief = [belief for belief in user_beliefs if belief['belief']['belief_id'] == belief_id][0]
        return Belief().from_dict(user_belief)

    @staticmethod
    def save_belief_data(dialog: Dialog, user_telegram_id: int, belief_id: int):
        dialog.executed_time.end_time = datetime.now().time().strftime("%H:%M:%S")
        user = Client.objects(telegram_id=user_telegram_id).get()
        user_beliefs = user.beliefs
        user_belief = [belief for belief in user_beliefs if belief['belief']['belief_id'] == belief_id][0]
        index = user_beliefs.index(user_belief)
        user.beliefs[index]['dialogs'].append(dialog.to_dict())
        user.beliefs[index]['number_of_passages'] += 1
        try:
            user.save()
            print(f"Данные: {user_belief}\n"
                  f"Для пользователя: {user_telegram_id}\n"
                  f"Cохранены успешено ")
        except Exception as e:
            print(f"Что то пошло не так при сохранение данных для пользователя {user_telegram_id}\n", e.args, )


class MongoProblemsRepositoryORM(ProblemsRepository):
    def get_man_problems(self) -> list[Problem]:
        return Problem.objects(sex="man")

    @staticmethod
    def get_man_problems_by_category(category_name_id: str) -> list[Problem]:
        return Problem.objects(sex="man", category_id=category_name_id)

    def get_woman_problems(self) -> list[Problem]:
        return Problem.objects(sex="woman")

    @staticmethod
    def get_woman_problems_by_category(category_name_id: str) -> list[Problem]:
        return Problem.objects(sex='woman', category_id = category_name_id)

    @staticmethod
    def get_problem_by_problem_id(belief_id: int) -> Problem:
        """
        Функция обращается к базе данных и отдает 1 проблему по ее id
        """
        print(Problem.objects(belief_id=belief_id).get())
        return Problem.objects(belief_id=belief_id).get()


class MongoDataBaseRepository(MongoDataBaseRepositoryInterface):

    def __init__(self, client_repository: MongoClientUserRepositoryORM,
                 problem_repository: MongoProblemsRepositoryORM):
        self.client_repository = client_repository
        self.problem_repository = problem_repository

    def client_repository(self):
        return self.client_repository

    def problem_repository(self):
        return self.problem_repository
