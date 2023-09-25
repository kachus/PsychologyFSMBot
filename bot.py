import asyncio
from aiogram import Bot, Dispatcher
import logging
from BD.DBinterface import ClientRepository
from BD.MongoDB.mongo_db import MongoClientUserRepositoryORM, MongoDB, MongoORMConnection
from hadnlers import command_handlers, define_belif_handlers
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import Config, load_config


logger = logging.getLogger(__name__)


async def main():
    # logging config
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')

    # info about starting the bot
    logger.info('Starting bot')

    config: Config = load_config()

    #инициализируем базу данных
    MongoORMConnection(config.data_base)
    data_base = MongoClientUserRepositoryORM()
    storage: MemoryStorage = MemoryStorage()

    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

    dp = Dispatcher(data_base=data_base)
    # dp: Dispatcher = Dispatcher()
    dp.include_router(command_handlers.router)
    dp.include_router(define_belif_handlers.router)
    # register_all_handlers(dp)
    # await set_main_menu(dp)

    try:
        await dp.start_polling(bot)
    finally:
        bot.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')
        # Выводим в консоль сообщение об ошибке,
        # если получены исключения KeyboardInterrupt или SystemExit


