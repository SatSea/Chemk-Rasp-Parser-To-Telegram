import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from log import logger

async def cat_pic():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://meow.senither.com/v1/random') as response:
            text = await response.text()
    cat = json.loads(text)
    return cat['data']['url'], cat['data']['type']

def create_task(task):
    asyncio.create_task(task)
    
async def sleep(time):
    logger.info(f"Current time: {datetime.now()} Sleep time: {timedelta(seconds=time)}   Sleep until: {datetime.fromtimestamp(datetime.timestamp(datetime.now())+time)}")
    return await asyncio.sleep(time)