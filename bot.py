import asyncio
from aiogram import Bot, Dispatcher
import logging
from container import data_base_controller, config, logger
from hadnlers import command_handlers, deep_process_new, \
    chose_existing_belief_handlers, \
    show_statistic_handler
from aiogram.fsm.storage.redis import RedisStorage, Redis


async def main():
    # logging config
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')

    # info about starting the bot
    logger.info('Starting bot')
    redis = Redis(host=config.redis_storage.docker_host,
                  port=config.redis_storage.docker_port)
    storage: RedisStorage = RedisStorage(redis=redis)

    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

    dp = Dispatcher(data_base=data_base_controller, storage=storage)
    # dp: Dispatcher = Dispatcher()
    dp.include_router(command_handlers.router)
    dp.include_router(deep_process_new.router)
    # dp.include_router(deep_process_handers.router)
    dp.include_router(chose_existing_belief_handlers.router)
    dp.include_router(show_statistic_handler.router)
    # dp.include_router(define_belif_handlers.router)
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
