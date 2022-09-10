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
load_dotenv("Tokens.env")
TOKEN = os.getenv('TOKEN')
bot = AsyncTeleBot(TOKEN)
today = tomorrow = None
# endregion


def get_rsp(day):
    contents, schedule_on_site = get_from_site(day)
    if(schedule_on_site is None):
        return "Мне не удалось найти расписание на сайте :("

    nomer_pari, nazvanie_para, kabunet_pari = [], [], []
    try:
        tables = pd.read_html(contents)
    except:
        return "Расписание есть на сайте, но у меня не получилось его разобрать на таблицы :("
    try:
        for index in range(len(tables[1][0])):
            group = tables[1][0][index]
            if group == "Ир1-20":
                nomer_pari.append(tables[1][1][index])
                nazvanie_para.append(tables[1][2][index])
                kabunet_pari.append(tables[1][3][index])
    except:
        try:
            for index in range(len(tables[0])):
                group = tables[0][0][index]
                if group == "Ир1-20":
                    nomer_pari.append(tables[0][1][index])
                    nazvanie_para.append(tables[0][2][index])
                    kabunet_pari.append(tables[0][3][index])
        except:
            return "Расписание есть на сайте, но у меня не получилось его разобрать :("
    itogo = gen_message(nomer_pari, nazvanie_para, kabunet_pari)
    return itogo

def get_from_site(day):
    responce = requests.get(f"https://rsp.chemk.org/4korp/{day}.htm")
    responce.encoding = 'windows-1251'
    contents = responce.text
    soup = BeautifulSoup(contents, "html.parser")
    schedule_on_site = not (soup.find("div", class_="Section1"))
    return contents,schedule_on_site


def gen_message(nomer_pari, nazvanie_para, kabunet_pari):
    para = []
    for index in range(len(nomer_pari)):
        para.append(
            f"Номер пары: {nomer_pari[index]}  Пара: {nazvanie_para[index]}  Кабинет: {kabunet_pari[index]}\n")
    pervaia_para = f"Приходить к {nomer_pari[0]} паре\n\n"
    itogo = pervaia_para+(''.join(para))
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
        tables = pd.read_html(contents)
        if tables != None:
            resp = []
            for index in range(len(tables[1][0])):
                group = tables[1][0][index]
                if group == "Ир1-20":
                    resp[0].append(tables[1][1][index])
                    resp[1].append(tables[1][2][index])
                    resp[2].append(tables[1][3][index])
            return gen_message[resp[0], resp[1], resp[2]]
    except:
        print("Чекнул, чуть не умер, но выжил")
    else:
        print("Чекнул, не нашел расписание")


async def dispatch(id, rasp):
    bot.send_message(id, rasp)


async def wait(time):
    print(f"Current time: {datetime.datetime.now()} Sleep time: {datetime.timedelta(seconds=time)}   Sleep until: {datetime.datetime.fromtimestamp(datetime.datetime.timestamp(datetime.datetime.now())+time)}")
    return await asyncio.sleep(time)


@bot.message_handler(commands=["FAQ"])
async def FAQ(message: types.Message):
    create_task(bot.reply_to(message, """FAQ: 
                                     1)Q: Почему бот такой кривой?
                                     A: Потому что, бюджет размером в банку пива и разрабатывал все это долбоеб(ка) на разработке
                                     2)Q: Поддержка других групп?
                                     A: Да, попытаюсь сделать в течении месяца
                                     2)Q: Поддержка других корпусов?
                                     A: Нет, потому что у меня хватит сил на такую большую переделку кода (у них там таблицы с расписание парсить слишком трудно...)
                                     3)Q: Сколько будет работать этот бот?
                                     A: Да
                                     4)Q: Код будет выложен?
                                     A: Нет, мне его стыдно показывать
                                     5)Q: Почему бот иногда так долго отвечает?
                                     A: а)Бот недавно перезапускался и у него пустой кэш
                                     б) Период рассылки сообщений
                                     в) Опять сайт ЧЭМК ограничил скорость для меня
                                     г) Я накосячил где-то (Поймите и простите)
                                     д) Бот ушел опять в бесконечную петлю
                                     6)Q: У меня есть идея/заметил баг, как мне связаться?
                                     A: Странное желание, но вот
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


@bot.message_handler(commands=["Subscribe"])
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


@bot.message_handler(commands=["Today"])
async def cmd_start(message: types.Message):
    rasp = get_rsp("Today")
    asyncio.create_task(dump_logs(
        f"Issued \"Today\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, rasp)


@bot.message_handler(commands=["Tomorrow"])
async def cmd_start(message: types.Message):
    rasp = get_rsp("Tomorrow")
    asyncio.create_task(dump_logs(
        f"Issued \"Tomorrow\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, rasp)


@bot.message_handler(func=lambda message: True)
async def unknown_command(message):
    await bot.reply_to(message, "Неизвестная комманда")


async def init():
    asyncio.create_task(bot.polling())
    print("Я не завис")
    await asyncio.create_task(waiter_checker())


if __name__ == "__main__":
    asyncio.run(init())
