from dataclasses import dataclass
from environs import Env


@dataclass
class MongoDB:
    bd_name: str
    host: str
    port: int


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class Config:
    tg_bot: TgBot
    data_base: MongoDB


def load_config(path: str or None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  data_base=MongoDB(bd_name=env('DATABASE'),
                                    host=env('DB_HOST'),
                                    port=int(env('DB_PORT')))
                  )
