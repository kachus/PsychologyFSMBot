from datetime import datetime

from BD.MongoDB.mongo_enteties import Client
from aiogram.types import Message


async def save_user_if_not_exist(message: Message, data_base) -> None:
    try:
        if not data_base.check_client_in_database(message.chat.id):
            data_base.save_client_to_database(Client(
                telegram_id=message.chat.id,
                name=message.from_user.first_name,
                date_of_first_using=datetime.now(),
                date_of_last_visiting=datetime.now(),
                answers=[]
            ))
            if data_base.check_client_in_database(message.chat.id):
                print(f"Пользовтель c id: {message.chat.id,} \nименем: {message.from_user.first_name} добавлен в базу")
    except Exception as e:
        print('что то не так с сохранением нового пользователя в базу данных')
