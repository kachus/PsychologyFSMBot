# Контейнер для Dependency Injection. В этом контейнере инициализируются все классы
# _________________________________
import logging
import os

from BD.MongoDB.mongo_db import MongoClientUserRepositoryORM, \
    MongoProblemsRepositoryORM, MongoDataBaseRepository, MongoORMConnection

from config_data.config import Config, load_config

# Инициализируем logger
logger = logging.getLogger(__name__)
# Конфиги из .env
config: Config = load_config()
# создаем Коннект к базе данных
MongoORMConnection(config.data_base)
# создаем клиентский репозиторий
client_repo = MongoClientUserRepositoryORM()
# создаем проблемный репозиторий
problem_repo = MongoProblemsRepositoryORM()
# Создаем общий репозиторий
data_base_controller = MongoDataBaseRepository(client_repository=client_repo,
                                               problem_repository=problem_repo)
#Путь к корневой папке относительно файла container. Так жк нормализую путь для соответсвия на разных системах
root_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))