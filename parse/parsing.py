import json
from cachetools import cached, TTLCache
from parse.requester import get_table_rasp


@cached(cache=TTLCache(maxsize=1024, ttl=1800))
async def group_rasp(day: str,name_group: str) -> str:
    return await get_rasp_group(day)[name_group]
    
@cached(cache=TTLCache(maxsize=1024, ttl=1800))
async def get_rasp_group(day: str) -> list[str]: 
    '''
    To avoid having to тыкать parser every time, 
    perhaps there was an easier way than to create another function 
    and cache it, but it didn't come to my head straight off
    '''
    return await rasp(day)                       

async def rasp(day: str) -> list[str]:
    rasp = {}
    table = get_table_rasp(day)
    rasp["day"] = table[0][0][33:] # 33 - "Распоряжение по учебной части на "
    for line in table[3:]:
        name_group, lession_num, lession_name, lession_kab = line # ебнет? не должно
        if(lession_num != lession_num):  # (nan != nan)
            current_group = None
            continue
        if name_group == name_group: current_group = name_group
        if current_group[:6] not in rasp: rasp[current_group[:6]] = [] 
        match line[2]:                                          
            case "Нет":
                rasp[current_group].append(f"Пара {lession_num} отменена")
            case "По расписанию":
                rasp[current_group].append(await get_default_rasp(current_group, lession_num, day, lession_kab))
            case "День самостоятельной работы":
                rasp[current_group].append(f"День самостоятельной работы")
            case _:
                if(current_group[-3:] == "п/г"):
                    rasp[current_group[:6]].append(f"Для {current_group[-5:]} Номер пары: {lession_num}  Пара: {lession_name}  Кабинет: {lession_kab}")
                else:
                    rasp[current_group].append(f"Номер пары: {lession_num}  Пара: {lession_name}  Кабинет: {lession_kab}")
    return rasp

@cached(cache = {})
async def load_json_plain_rasp():
    async with open("plain_rasp.json", "r", encoding="utf-8") as rasp:
        return json.load(rasp)

async def get_default_rasp(name_group:str, lession_num:str|int, day: str, non_default_kab: str = None):
    return "Дефолтное расписание"