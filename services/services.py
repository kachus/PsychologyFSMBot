from datetime import datetime
from typing import Any

from BD.DBinterface import MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_enteties import Client
from aiogram.types import Message


async def save_user_if_not_exist(message: Message, data_base: MongoDataBaseRepositoryInterface) -> None:
    try:
        if not data_base.client_repository.check_client_in_database(message.chat.id):
            data_base.client_repository.save_client_to_database(Client(
                telegram_id=message.chat.id,
                name=message.from_user.first_name,
                date_of_first_using=datetime.now(),
                date_of_last_visiting=datetime.now(),
                answers=[]
            ))
            if data_base.client_repository.check_client_in_database(message.chat.id):
                print(f"Пользовтель c id: {message.chat.id,} \nименем: {message.from_user.first_name} добавлен в базу")
    except Exception as e:
        print('что то не так с сохранением нового пользователя в базу данных')


async def save_answer(message: Message,
                      data_to_save: Any,
                      data_base: MongoDataBaseRepositoryInterface):
    answer = {}
    answer['define_problem'] = {
        'answer_date': datetime.now(),
        'client_answers': data_to_save}
    try:
        data_base.client_repository.save_all_client_answers_by_id(message.chat.id,answer)
        print(f"Ответ: {answer} \n от пользователя"
              f" {message.from_user.first_name} \n{message.chat.id} "
              f"\nСохранен в базу даных ")
    except Exception as e:
        print(e, "\n что то пошло не так при сохранении ответа")


