import asyncio
import aiohttp
import json

async def cat_pic():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://meow.senither.com/v1/random') as response:
            text = await response.text()
    cat = json.loads(text)
    return cat['data']['url'], cat['data']['type']

def create_task(task):
    asyncio.create_task(task)