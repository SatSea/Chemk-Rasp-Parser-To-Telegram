import asyncio
import json
import os
import requests
import pandas as pd
from telebot import types
from bs4 import BeautifulSoup
from telebot.async_telebot import AsyncTeleBot
import datetime
from dotenv import load_dotenv


# region some needed vars
load_dotenv("Env/Tokens.env")
TOKEN = os.getenv('TOKEN')
bot = AsyncTeleBot(TOKEN)
today = tomorrow = None

# endregion

def plain_rasp(day):
    with open("plain_rasp.json", "r", encoding="utf-8") as rasp:
        raspisanie = rasp.read()
        all_rasp = json.loads(raspisanie)
    return all_rasp["groups"]["ir1-20"][day]

def default_rasp(plain_raspisanie):
    paras = []
    for para in range(len(plain_raspisanie)):
        if(len(plain_raspisanie[para]) != 0): paras.append(f"Номер пары: {para+1}  Пара: {plain_raspisanie[para][0]}, {plain_raspisanie[para][1]} Кабинет: {plain_raspisanie[para][2]}")
    schedule = "\n".join(paras)
    return schedule

def get_rsp(day):
    contents, schedule_on_site = get_from_site(day)
    para = []
    has_group = False
    if(schedule_on_site is None):
        return "Мне не удалось найти расписание на сайте :("
    if(day == "Today"):
        plain_raspisanie = plain_rasp(datetime.datetime.today().strftime('%A'))
    else:
        plain_raspisanie = plain_rasp((datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%A'))
    try:
        tables = pd.read_html(contents,thousands=None)
    except:
        return "Расписание есть на сайте, но у меня не получилось его разобрать на таблицы :("
    try:
        for index in range(len(tables[1])):
            group = tables[1][0][index]
            if group == "Ир1-20":
                has_group = True
                paras = tables[1][2][index]
                if (paras == "По расписанию"):
                        for nomer in (tables[0][1][index]).split(','):
                            para.append(f"Номер пары: {nomer}  Пара: {plain_raspisanie[0][2][nomer]} Кабинет: {plain_raspisanie[0][3][nomer]}")
                elif (paras == "Нет"):
                    para.append(f"Номер пары: {tables[1][1][index]}  Пара: отменена")
                else:
                    para.append(
            f"Номер пары: {tables[1][1][index]}  Пара: {tables[1][2][index]}  Кабинет: {tables[1][3][index]}\n")
    except:
        try:
            for index in range(len(tables[0])):
                group = tables[0][0][index]
                if group == "Ир1-20":
                    has_group = True
                    paras = tables[0][2][index]
                    if (paras == "По расписанию"):
                        for nomer in (tables[0][1][index]).split(','):
                            nomer = int(nomer) - 1
                            para.append(f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                    elif (paras == "Нет"):
                        para.append(f"Номер пары: {tables[0][1][index]}  Пара: отменена")
                    else:
                        para.append(
                f"Номер пары: {tables[0][1][index]}  Пара: {tables[0][2][index]}  Кабинет: {tables[0][3][index]}\n")
        except:
            return "Расписание есть на сайте, но у меня не получилось его разобрать :("
    if(has_group):
        itogo = gen_message(para)
    else:
        itogo = default_rasp(plain_raspisanie)
    return itogo

def get_from_site(day):
    responce = requests.get(f"https://rsp.chemk.org/4korp/{day}.htm")
    responce.encoding = 'windows-1251'
    contents = responce.text
    soup = BeautifulSoup(contents, "html.parser")
    schedule_on_site = not (soup.find("div", class_="Section1"))
    return contents,schedule_on_site


def gen_message(para):
    # para = []
    # pervaia_para = f"Приходить к {nomer_pari[0]} паре\n\n"
    itogo = ('\n'.join(para))
    return itogo


async def waiter_checker():
    while(True):
        print("Считаю сколько спать")
        time_to_sleep = (datetime.datetime.now().replace(
            hour=9, minute=30, second=0, microsecond=0) + datetime.timedelta(1) - datetime.datetime.now())
        seconds_to_sleep = time_to_sleep.seconds
        await wait(seconds_to_sleep)
        resp = None
        while(resp == None):
            resp = checker()
            if resp == None:
                await wait(300)
        with open("config.json", "r") as config:
            ids = json.loads(config.read())
            print(ids[0]["id"])
            for id in ids[0]["id"]:
                dispatch(id, resp)


async def dump_logs(logging_info):
    print(f"Writted to logs")
    with open("plain_logging.log", "a") as log:
        log.write(logging_info)


def checker():
    print("Чекаю расписание")
    
    try:
        contents, schedule_on_site = get_from_site("tomorrow")
        if(schedule_on_site is None):
            return None
        tables = pd.read_html(contents,thousands=None)
        para = []
        has_group = False
        plain_raspisanie = plain_rasp(datetime.datetime.today().strftime('%A'))
        try:
            for index in range(len(tables[1])):
                group = tables[1][0][index]
                if group == "Ир1-20":
                    has_group = True
                    paras = tables[1][2][index]
                    if (paras == "По расписанию"):
                            for nomer in (tables[0][1][index]).split(','):
                                para.append(f"Номер пары: {nomer}  Пара: {plain_raspisanie[0][2][nomer]} Кабинет: {plain_raspisanie[0][3][nomer]}")
                    elif (paras == "Нет"):
                        para.append(f"Номер пары: {tables[1][1][index]}  Пара: отменена")
                    else:
                        para.append(
                f"Номер пары: {tables[1][1][index]}  Пара: {tables[1][2][index]}  Кабинет: {tables[1][3][index]}\n")
        except:
            try:
                for index in range(len(tables[0])):
                    group = tables[0][0][index]
                    if group == "Ир1-20":
                        has_group = True
                        paras = tables[0][2][index]
                        if (paras == "По расписанию"):
                            for nomer in (tables[0][1][index]).split(','):
                                nomer = int(nomer) - 1
                                para.append(f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        elif (paras == "Нет"):
                            para.append(f"Номер пары: {tables[0][1][index]}  Пара: отменена")
                        else:
                            para.append(
                    f"Номер пары: {tables[0][1][index]}  Пара: {tables[0][2][index]}  Кабинет: {tables[0][3][index]}\n")
            except:
                return "Расписание есть на сайте, но у меня не получилось его разобрать :("
        if(has_group):
            itogo = gen_message(para)
        else:
            itogo = default_rasp(plain_raspisanie)
    except:
        print("Чекнул, чуть не умер, но выжил")
    else:
        print("Чекнул, не нашел расписание")


async def dispatch(id, rasp):
    bot.send_message(id, rasp)


async def wait(time):
    print(f"Current time: {datetime.datetime.now()} Sleep time: {datetime.timedelta(seconds=time)}   Sleep until: {datetime.datetime.fromtimestamp(datetime.datetime.timestamp(datetime.datetime.now())+time)}")
    return await asyncio.sleep(time)


@bot.message_handler(commands=["FAQ","faq"])
async def FAQ(message: types.Message):
    create_task(bot.reply_to(message, """FAQ: 
 1)Q: Почему бот такой кривой?
    A: Потому что, бюджет размером в банку пива и разрабатывал все это долбоеб(ка) на разработке
 2)Q: Поддержка других групп?
    A: Да, попытаюсь сделать в течении месяца
 3)Q: Поддержка других корпусов?
    A: Нет, потому что у меня хватит сил на такую большую переделку кода (у них там таблицы с расписание парсить слишком трудно...)
 4)Q: Сколько будет работать этот бот?
    A: Да
 5)Q: Код будет выложен?
    A: Нет, мне его стыдно показывать (но когда-нибудь потом возможно выложу)
 6)Q: Почему бот иногда так долго отвечает?
    A: а)Бот недавно перезапускался и у него пустой кэш
    б) Период рассылки сообщений
    в) Опять сайт ЧЭМК ограничил скорость для меня
    г) Я накосячил где-то (Поймите и простите)
    д) Бот ушел опять в бесконечную петлю
 7)Q: Логируется ли какая-либо информация?
    A: Да, логируется минимальное количество информации (Ник, время, исполненная команда, статус выполнения команды)
    Данные удаляются по первому требованию пользователя. 
 8)Q: У меня есть идея/заметил баг, как мне связаться?
    A: Странное желание, но вот (и пожалуйста не пишите мне другим способом)
 satsea388@gmail.com / https://t.me/satsea / Aestas#0577""")
)

def create_task(task):
    asyncio.create_task(task)

@bot.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/FAQ","/Today", "/Tomorrow", "/Subscribe"]
    keyboard.add(*buttons)
    asyncio.create_task(dump_logs(
        f"Issued \"start\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, """Disclaimer: Данный бот не выдает истины последней инстанции, вся информация выданная ботом предоставляется на условиях \"как есть\" без каких-либо гарантий полноты, точности. Не заменяет просмотр расписания на сайте, а также не является официальным проектом.
Бот все еще находится стадии очень ранней разработки. Поэтому могут быть случайные сообщения и некоторые неточности.
Аптайм бота очень зависит от моего настроения и поэтому бот может быть не всегда доступен 24/7 :)""", reply_markup=keyboard)

@bot.message_handler(commands=["Subscribe","subscribe"])
async def cmd_start(message: types.Message):
    asyncio.create_task(dump_logs(
        f"Issued \"Today\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    # try:
    chat_id = message.chat.id
    if(not os.path.isfile("config.json")):
        open("config.json", "x").close()
    with open("config.json", "r") as config:
        size_file = os.stat("config.json").st_size > 0
        if(size_file):
            configs = json.loads(config.read())
            with open("config.json", "w") as config:
                ids = configs[0]["id"]
                if(chat_id in ids):
                    try:
                        ids.remove(chat_id)
                    except:
                        asyncio.create_task(bot.reply_to(
                            message, "[WIP]Не получилось отписаться от обновлений расписания"))
                    else:
                        asyncio.create_task(bot.reply_to(
                            message, "[WIP]Успешно получилось отписаться от обновление расписания"))
                else:
                    ids.append(chat_id)
                    asyncio.create_task(bot.reply_to(
                        message, "[WIP]Успешно подписан на обновление расписания"))
                json1 = json.dumps([{"id": ids}])
                configs[0]["id"] = json1
                config.write(configs)
        else:
            ids = []
            ids.append(chat_id)
            json1 = json.dumps([{"id": ids}])
            with open("config.json", "w") as config:
                try:
                    ids = configs[0]["id"]
                    configs[0]["id"] = json1
                    config.write(configs)
                    asyncio.create_task(bot.reply_to(
                        message, "[WIP]Успешно подписан на обновление расписания"))
                except:
                    config.write(json1)
                    asyncio.create_task(bot.reply_to(
                        message, "[WIP]Успешно подписан на обновление расписания"))


@bot.message_handler(commands=["Today","today"])
async def cmd_start(message: types.Message):
    rasp = get_rsp("Today")
    asyncio.create_task(dump_logs(
        f"Issued \"Today\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, rasp)


@bot.message_handler(commands=["Tomorrow","tomorrow"])
async def cmd_start(message: types.Message):
    rasp = get_rsp("Tomorrow")
    asyncio.create_task(dump_logs(
        f"Issued \"Tomorrow\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, rasp)


@bot.message_handler(func=lambda message: True)
async def unknown_command(message):
    await bot.reply_to(message, "Я не нашел такую команду...")
    await bot.send_animation(message.chat.id,r'https://cdn.discordapp.com/attachments/878333995908222989/1019257151916625930/not_found.gif')


async def init():
    asyncio.create_task(bot.polling())
    print("Я не завис")
    await asyncio.create_task(waiter_checker())


if __name__ == "__main__":
    asyncio.run(init())
