from datetime import datetime
from pathlib import Path
from typing import Any
import os
from BD.DBinterface import MongoDataBaseRepositoryInterface
from BD.MongoDB.mongo_enteties import Client
from aiogram.types import Message
from aiogram import Bot


async def save_user_if_not_exist(message: Message, data_base: MongoDataBaseRepositoryInterface) -> None:
    try:
        if not data_base.client_repository.check_client_in_database(message.chat.id):
            data_base.client_repository.save_client_to_database(Client(
                telegram_id=message.chat.id,
                name=message.from_user.first_name,
                date_of_first_using=datetime.now(),
                date_of_last_visiting=datetime.now(),
                beliefs=[]

            ))
            if data_base.client_repository.check_client_in_database(message.chat.id):
                print(f"Пользовтель c id: {message.chat.id,} \nименем: {message.from_user.first_name} добавлен в базу")
    except Exception as e:
        print(e.message, e.args,
              'что то не так с сохранением нового пользователя в базу данных')


async def save_answer(message: Message,
                      data_to_save: Any,
                      data_base: MongoDataBaseRepositoryInterface):
    answer = {}
    answer['define_problem'] = {
        'answer_date': datetime.now(),
        'client_answers': data_to_save}
    try:
        data_base.client_repository.save_all_client_answers_by_id(message.chat.id, answer)
        print(f"Ответ: {answer} \n от пользователя"
              f" {message.from_user.first_name} \n{message.chat.id} "
              f"\nСохранен в базу даных ")
    except Exception as e:
        print(e.message, "\n что то пошло не так при сохранении ответа")


async def load_voice_messages(message: Message, bot: Bot):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(Path.cwd(), 'user_voices', f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())
    return file_on_disk
