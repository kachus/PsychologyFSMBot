from dataclasses import dataclass
from environs import Env


@dataclass
class MongoDB:
    bd_name: str
    # для пользования на локальной машине
    local_port: int
    local_host: int | str
    # для пользования на сервере в доккере
    docker_port: int
    docker_host: int | str


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
@dataclass
class RedisStorage:
    # для пользования на локальной машине
    local_port: int
    local_host: int | str
    # для пользования на сервере в доккере
    docker_port: int
    docker_host: int | str


@dataclass
class Config:
    tg_bot: TgBot
    data_base: MongoDB
    redis_storage : RedisStorage


def load_config(path: str or None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  data_base=MongoDB(bd_name=env('DATABASE'),
                                    local_port=env('MONGO_DB_LOCAL_PORT'),
                                    local_host=int(env('MONGO_DB_LOCAL_HOST')),
                                    docker_port=(env('MONGO_DB_DOCKER_PORT')),
                                    docker_host=(env('MONGO_DB_DOCKER_HOST')),
                                    ),
                  redis_storage=(RedisStorage(
                      local_port=env('REDIS_LOCAL_PORT'),
                      local_host=env('REDIS_LOCAL_HOST'),
                      docker_port=env('REDIS_DOCKER_PORT'),
                      docker_host=env('REDIS_DOCKER_HOST'),
                  ))
                  )
