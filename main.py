from asyncio import create_task, run
from datetime import datetime

from dispatcher.rasp_checker import start_waiting

from log import logger
from init_bot import bot, dp
from handlers import regular
from keyboard import callbacks


# region some needed varibles
start_time = datetime.now()
# endregion


async def bot_start():
    try:
        create_task(start_waiting())
        await dp.start_polling(bot)
    except:
        logger.error("Bot has failed to start")

async def main():
    await regular.register_regular_handlers(dp)
    await callbacks.register_callbacks(dp)
    await bot_start()


if __name__ == "__main__":
    run(main())