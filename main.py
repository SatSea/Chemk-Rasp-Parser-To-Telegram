import asyncio
import json
from aiogram import types
from aiogram.utils import executor
from aiogram.utils.markdown import escape_md
import requests
from datetime import datetime

from log import logger
from misc import create_task
import Env
from init_bot import init_bot, dp
from handlers import regular


# region some needed varibles
start_time = datetime.now()
# endregion


async def bot_start():
    try:
        await dp.start_polling(init_bot)
    except:
        logger.error("Bot has failed to start")

async def main():
    await regular.register_regular_handlers(dp)
    await bot_start()


if __name__ == "__main__":
    asyncio.run(main())