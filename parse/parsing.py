from cachetools import cached, TTLCache

async def group_today_rasp(name_group):
    return await today_rasp()[name_group]

async def group_tomorrow_rasp(name_group):
    return await tomorrow_rasp()[name_group]
    
@cached(cache=TTLCache(ttl=3600))
async def today_rasp():
    return await rasp("today")

@cached(cache=TTLCache(ttl=3600))
async def tomorrow_rasp():
    return await rasp("tomorrow") 

async def rasp(day: str) -> str:
    return "Затычка"


async def new_parsing_eng(table: list, day: str = "Tommorow") -> list[str]:
    rasp = {}
    rasp["day"] = table[0][0][33:] # 33 символа - "Распоряжение по учебной части на "
    for line in table[3:]:
        name_group, lession_num, lession_name, lession_kab = line # ебнет? не должно
        if(lession_num != lession_num):  # проверка на пустую клетку номера пары (nan != nan)
            current_group = None         # если номер пары пустой, то считаем что нет группы и пар
            continue                     # так что пропускаем
        if name_group == name_group: current_group = name_group # если есть название группы
                                                                # то сохраняем на случай кривой разметки расписания
        if current_group[:6] not in rasp: rasp[current_group[:6]] = [] # первые 6 символов название группы без подргуппы
        match line[2]:                                          
            case "Нет":
                rasp[current_group].append(f"Пара {lession_num} отменена")
            case "По расписанию":
                rasp[current_group].append(get_default_rasp(current_group, lession_num, day, lession_kab))
            case "День самостоятельной работы":
                rasp[current_group].append(f"День самостоятельной работы")
            case _:
                if(current_group[-3:] == "п/г"):
                    rasp[current_group[:6]].append(f"Для {current_group[-5:]} Номер пары: {lession_num}  Пара: {lession_name}  Кабинет: {lession_kab}")
                else:
                    rasp[current_group].append(f"Номер пары: {lession_num}  Пара: {lession_name}  Кабинет: {lession_kab}")
    return rasp

def get_default_rasp(name_group:str, lession_num:str|int, day: str, non_default_kab: str = None):
    return "Дефолтное расписание"