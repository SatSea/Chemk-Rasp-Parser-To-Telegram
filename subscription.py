from json import load, dump
from misc import create_task
from log import logger

async def load_json() -> None:
    with open("Env/subscription.json", "r", encoding="utf-8") as json:
        return load(json)

async def write_json(data: str) -> None:
    with open("Env/subscription.json", "w+", encoding="utf-8") as json:
        return dump(data, json, ensure_ascii=False)

async def get_subs(user_id: str) -> list:
    subs = await load_json()
    if (user_id in subs): return subs[user_id]
    return []
   
async def set_sub(user_id: int, group: str) -> None:
    subs = await load_json()
    user_id = str(user_id)
    if(user_id not in subs): subs[user_id] = []
    if(group in subs[user_id]):
        subs[user_id].remove(group)
    else:
        subs[user_id].append(group)
    create_task(write_json(subs))
    