import json
from parse.requester import get_table_rasp
from subscription import get_message_type 
from aiocache import cached
from aiocache.serializers import PickleSerializer
    
async def group_rasp(day: str,name_group: str, user_id: int) -> str:
    rasp_non_formated = await get_rasp_group(day)
    return await format_message(user_id, rasp_non_formated[name_group], rasp_non_formated["day"], name_group)

async def get_rasp_group(day: str) -> list[str]:
    '''
    To avoid having to тыкать parser every time, 
    perhaps there was an easier way than to create another function 
    and cache it, but it didn't come to my head straight off
    '''
    if (day == "today"):
        return await get_rasp_today()
    return await get_rasp_tomorrow()
    

@cached(ttl=1800, serializer=PickleSerializer())
async def get_rasp_today() -> list[str]:
    return await rasp("today")

@cached(ttl=1800, serializer=PickleSerializer())
async def get_rasp_tomorrow() -> list[str]:
    return await rasp("tomorrow")

async def rasp(day: str) -> list[str]:
    rasp = {}
    table = await get_table_rasp(day)
    rasp["day"] = table[0][0][33:] # 33 - "Распоряжение по учебной части на "
    for line in table[3:]:
        name_group, para, lession_name, lession_kab = line if len(line) == 4 else (*line, None) # ебнет? не должно
        if(para != para):  # (nan != nan)
            current_group = None
            continue
        for lession_num in para.split(','):
            if name_group == name_group: current_group = name_group
            if current_group[:6] not in rasp: rasp[current_group[:6]] = [] 
            match lession_name:                                          
                case "Нет":
                    rasp[current_group].append(f"{lession_num}-ая пара отменена" if lession_num != 3 else "{lession_num}-ья пара отменена")
                case "По расписанию":
                    rasp[current_group].append(await get_default_rasp(current_group, lession_num, day, lession_kab))
                case "День самостоятельной работы":
                    rasp[current_group].append(f"День самостоятельной работы")
                case _:
                    if(current_group[-3:] == "п/г"):
                        rasp[current_group[:6]].append([current_group[-5:], lession_num, lession_name, lession_kab])
                    else:
                        rasp[current_group].append([lession_num, lession_name, lession_kab])
                        
    return rasp

@cached(serializer=PickleSerializer())
async def load_json_plain_rasp():
    async with open("plain_rasp.json", "r", encoding="utf-8") as rasp:
        return json.load(rasp)

async def get_default_rasp(name_group:str, lession_num:str|int, day: str, non_default_kab: str = None):
    return "Дефолтное расписание"

async def format_message(user_id: int, rasp: str, day: str, group_name:str) -> str:
    match(await get_message_type(user_id)):
        case "Классический":
            formated_schedule = f"Расписание группы \"{group_name}\" на {day}:\n"
            template = ["Номер пары: {}   Пара: {}   Кабинет: {}","Для {} п/г Номер пары: {}   Пара: {}   Кабинет: {}"]
        case "Мини":
            formated_schedule = f"\"{group_name}\" на {day}:\n"
            template = ["{} | {} | {}","{} | {} | {} | {}"]
        case "Нормальный":
            formated_schedule = f"Расписание группы \"{group_name}\" на {day}:\n"
            template = ["Номер пары: {}\nПара: {}\nКабинет: {}","Для {} п/г Номер пары: {}\nПара: {}\nКабинет: {}"]
    for lession in rasp:
        if (len(lession) == 4): formated_schedule += (template[1]).format(*lession) +"\n"
        elif (len(lession) == 3): formated_schedule += (template[0]).format(*lession) +"\n"
        else: formated_schedule += lession +"\n"
    return formated_schedule
    