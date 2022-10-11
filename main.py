import asyncio
import datetime
import json
import os
from cachetools import cached, TTLCache

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import types
from telebot.async_telebot import AsyncTeleBot

# region disable some rules in pylint
# pylint: disable=anomalous-backslash-in-string, line-too-long, bare-except, missing-function-docstring, unspecified-encoding, broad-except
# endregion

# region some needed vars
load_dotenv("Env/Tokens.env")
TOKEN = os.getenv('TOKEN')
groups = os.getenv('GROUP')
name_of_group = os.getenv('NAME_OF_GROUP')
allowed_ids = list(map(int,os.getenv('ALLOWED_IDS').split(',')))
hour_when_start_checking = int(os.getenv('START_HOUR'))
bot = AsyncTeleBot(TOKEN)
TODAY = TOMORROW = None
weekday = ["Понедельник", "Вторник", "Среду", "Четверг", "Пятницу", "Субботу"]
month = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
         "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
# endregion


def plain_rasp(day):
    with open("plain_rasp.json", "r", encoding="utf-8") as rasp:
        raspisanie = rasp.read()
        all_rasp = json.loads(raspisanie)
    if day == "Sunday":
        day = "Monday"  # Даб,даб в воскресенье никто не учится
    return all_rasp["groups"][groups][day]


def default_rasp(plain_raspisanie):
    paras = []
    frist_para = None
    if plain_raspisanie == []:
        return "Согласно расписанию, в этот день нет пар"
    for para in range(len(plain_raspisanie)):
        if(len(plain_raspisanie[para]) != 0):
            if frist_para is None:
                frist_para = f"Приходить к {para +1} паре\n"
            paras.append(
                f"Номер пары: {para+1}  Пара: {plain_raspisanie[para][0]}, {plain_raspisanie[para][1]} Кабинет: {plain_raspisanie[para][2]}")
    schedule = frist_para + "\n".join(paras)
    return schedule


@cached(cache=TTLCache(maxsize=1024, ttl=3600))
def today_rasp():
    return get_rsp("Today")


@cached(cache=TTLCache(maxsize=1024, ttl=3600))
def tomorrow_rasp():
    return get_rsp("Tomorrow")


def get_rsp(day):
    if datetime.datetime.today().strftime('%A') == "Sunday" and day == "Today":
        return "Сегодня Воскресенье, какое раписание на сегодня?\nЧтобы узнать расписание на завтра используй /Tomorrow "
    contents, schedule_on_site = get_from_site(day)
    print("Я не кэширован!")
    para = []
    has_group = False
    if not schedule_on_site:
        return "На сайте пока что нет расписания :("
    if day == "Today":
        plain_raspisanie = plain_rasp(datetime.datetime.today().strftime('%A'))
    else:
        plain_raspisanie = plain_rasp(
            (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%A'))
    try:
        tables = pd.read_html(contents, thousands=None)
    except:
        return "Расписание есть на сайте, но у меня не получилось его разобрать на таблицы :("

    has_group = parsing_lines_to_schedule(para, plain_raspisanie, tables)
    if(has_group):
        itogo = gen_message(para)
    else:
        itogo = default_rasp(plain_raspisanie)
    if day == "Today":
        if datetime.datetime.today().weekday != 5:
            itogo = f"Расписание на {weekday[datetime.datetime.today().weekday()]} {datetime.datetime.today().day} {month[datetime.datetime.today().month-1]}:\n\n" + itogo
        else:
            itogo = f"Расписание на {weekday[(datetime.datetime.today() + datetime.timedelta(days=2)).weekday()]} {(datetime.datetime.today() + datetime.timedelta(days=2)).day} {month[(datetime.datetime.today() + datetime.timedelta(days=2)).month-1]}:\n\n" + itogo
    else:
        if datetime.datetime.today().weekday() != 5:
            itogo = f"Расписание на {weekday[(datetime.datetime.today() + datetime.timedelta(days=1)).weekday()]} {(datetime.datetime.today() + datetime.timedelta(days=1)).day} {month[(datetime.datetime.today() + datetime.timedelta(days=1)).month-1]}:\n\n" + itogo
        else:
            itogo = f"Расписание на {weekday[(datetime.datetime.today() + datetime.timedelta(days=2)).weekday()]} {(datetime.datetime.today() + datetime.timedelta(days=2)).day} {month[(datetime.datetime.today() + datetime.timedelta(days=2)).month-1]}:\n\n" + itogo
    return itogo


def parsing_lines_to_schedule(para, plain_raspisanie, tables):
    has_group = False
    if len(tables) > 1:  # выстрелит в колено если опять начнется мракобесие с таблицами
        for index in range(len(tables[1])):
            group = tables[1][0][index]
            if group == name_of_group:
                has_group = True
                paras = tables[1][2][index]
                if (paras == "По расписанию"):
                    for nomer in (tables[1][1][index]).split(','):
                        nomer = int(nomer) - 1
                        kab = tables[1][3][index]
                        if kab != kab:
                            para.append(
                                f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        else:
                            para.append(
                                f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {tables[1][3][index]}")
                elif (paras == "Нет"):
                    para.append(
                        f"Номер пары: {tables[1][1][index]}  Пара: отменена")
                else:
                    para.append(
                        f"Номер пары: {tables[1][1][index]}  Пара: {tables[1][2][index]}  Кабинет: {tables[1][3][index]}\n")
            elif group == (name_of_group + " 1 п/г") or (name_of_group + " 2 п/г"):
                has_group = True
                paras = tables[1][2][index]
                if (paras == "По расписанию"):
                    for nomer in (tables[1][1][index]).split(','):
                        nomer = int(nomer) - 1
                        kab = tables[1][3][index]
                        if kab != kab:
                            para.append(
                                f"Для {group[6:]} Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        else:
                            para.append(
                                f"Для {group[6:]}Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {tables[1][3][index]}")
                elif (paras == "Нет"):
                    para.append(
                        f"Номер пары: {tables[1][1][index]}  Пара: отменена")
                else:
                    para.append(
                        f"Номер пары: {tables[1][1][index]}  Пара: {tables[1][2][index]}  Кабинет: {tables[1][3][index]}\n")
    else:
        for index in range(len(tables[0])):
            group = tables[0][0][index]
            if group == name_of_group:
                has_group = True
                paras = tables[0][2][index]
                if (paras == "По расписанию"):
                    for nomer in (tables[0][1][index]).split(','):
                        nomer = int(nomer) - 1
                        kab = tables[0][3][index]
                        if kab != kab:
                            para.append(
                                f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        else:
                            para.append(
                                f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {tables[0][3][index]}")
                elif (paras == "Нет"):
                    para.append(
                        f"Номер пары: {tables[0][1][index]}  Пара: отменена")
                else:
                    para.append(
                        f"Номер пары: {tables[0][1][index]}  Пара: {tables[0][2][index]}  Кабинет: {tables[0][3][index]}\n")
            elif group == (name_of_group + "  1 п/г") or group == (name_of_group + "  2 п/г"):
                has_group = True
                paras = tables[0][2][index]
                if (paras == "По расписанию"):
                    for nomer in (tables[0][1][index]).split(','):
                        nomer = int(nomer) - 1
                        kab = tables[0][3][index]
                        if kab != kab:
                            para.append(
                                f"Для {group[8:]} Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        else:
                            para.append(
                                f"Для {group[8:]}Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {tables[1][3][index]}")
                elif (paras == "Нет"):
                    para.append(
                        f"Для {group[8:]} Номер пары: {tables[0][1][index]}  Пара: отменена")
                else:
                    para.append(
                        f"Для {group[8:]} Номер пары: {tables[0][1][index]}  Пара: {tables[0][2][index]}  Кабинет: {tables[0][3][index]}")

    return has_group


def get_from_site(day):
    responce = requests.get(f"https://rsp.chemk.org/4korp/{day}.htm")
    responce.encoding = 'windows-1251'
    contents = responce.text
    soup = BeautifulSoup(contents, "html.parser")
    schedule_on_site = not (soup.find("div", class_="Section1"))
    return contents, schedule_on_site


def gen_message(para):
    itogo = ('\n'.join(para))
    return itogo


async def waiter_checker():
    print("Поиск расписания запущен")
    while(True):
        print("Считаю сколько спать")
        weekday_number = datetime.datetime.today().weekday()
        if datetime.datetime.today().hour < hour_when_start_checking:
            time_to_sleep = datetime.datetime.now().replace(hour=hour_when_start_checking,
                                                            minute=0, second=0, microsecond=0) - datetime.datetime.now()
        else:
            if weekday_number != 5:
                time_to_sleep = (datetime.datetime.now().replace(hour=hour_when_start_checking, minute=0,
                                 second=0, microsecond=0) + datetime.timedelta(1) - datetime.datetime.now())
            else:
                time_to_sleep = (datetime.datetime.now().replace(hour=hour_when_start_checking, minute=0,
                                 second=0, microsecond=0) + datetime.timedelta(2) - datetime.datetime.now())
        seconds_to_sleep = time_to_sleep.total_seconds()
        await wait(seconds_to_sleep)
        resp = None
        while(resp is None):
            resp = checker()
            if resp is None:
                await wait(300)
        with open("config.json", "r") as config:
            ids = json.loads(config.read())
            print(ids[0]["id"])
            for people_id in ids[0]["id"]:
                create_task(dispatch(people_id, resp))


async def dump_logs(logging_info):
    print("Writted to logs")
    with open("plain_logging.log", "a") as log:
        log.write(logging_info)


def checker():
    print("Чекаю расписание")

    try:
        contents, schedule_on_site = get_from_site("tomorrow")
        if not schedule_on_site:
            return None
        tables = pd.read_html(contents, thousands=None)
        para = []
        has_group = False
        plain_raspisanie = plain_rasp(
            (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%A'))
        has_group = parsing_lines_to_schedule(para, plain_raspisanie, tables)
        if(has_group):
            itogo = gen_message(para)
        else:
            itogo = default_rasp(plain_raspisanie)
    except:
        print("Чекнул, чуть не умер, но выжил")
    tomorrow_rasp.cache_clear()
    weekday_number = datetime.datetime.today().weekday()
    tommorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    day_plus_two = datetime.datetime.today() + datetime.timedelta(days=2)
    if weekday_number != 5:
        itogo = f"Ежедневная рассылка расписания на {weekday[tommorrow.weekday()]} {tommorrow.day} {month[tommorrow.month-1]}:\n\n" + itogo
    else:
        itogo = f"Ежедневная рассылка расписания на {weekday[day_plus_two.weekday()]} {day_plus_two.day} {month[day_plus_two.month-1]}:\n\n" + itogo
    return itogo


async def dispatch(chat_id, rasp):
    await bot.send_message(chat_id, rasp)


async def wait(time):
    print(f"Current time: {datetime.datetime.now()} Sleep time: {datetime.timedelta(seconds=time)}   Sleep until: {datetime.datetime.fromtimestamp(datetime.datetime.timestamp(datetime.datetime.now())+time)}")
    return await asyncio.sleep(time)


@bot.message_handler(commands=["FAQ", "faq"])
async def FAQ(message: types.Message):
    create_task(bot.reply_to(message, """FAQ: 
1\)Q: Почему бот такой кривой?
  A: Потому что, бюджета не хватило даже на банку пива и разрабатывало все это долбоеб\(ка\) на разработке
2\)Q: Поддержка других групп?
  A: Когда\-нибудь поддержка других групп появится, но сейчас не планируется\.
3\)Q: Поддержка других корпусов?
  A: Нет, поддержки других корпусов не будет\.
4\)Q: Сколько будет работать этот бот?
  A: Да\.
5\)Q: Код будет выложен?
  A: https://github\.com/SatSea/Chemk\-Rasp\-Parser\-To\-Telegram
6\)Q: Почему бот иногда так долго отвечает?
  A: а\) Все таки одного ядро уже не хватает :\)
б\) Период рассылки сообщений
в\) Опять сайт ЧЭМК ограничил скорость для меня, опять\.\.\.\.
г\) Я накосячил где\-то \(Поймите и простите\)
д\) Бот ушел опять в бесконечную петлю
7\)Q: GDPR? \(aka Политика конфиденциальности\)
  A: Да, мы собираем некоторую информацию о пользователях \(Ник, время, исполненная команда, статус выполнения команды\)
  *Но данные удаляются по первому требованию пользователя или по истечению 30 дней \(Граждане ЕС не пользуйтесь этим ботом, пж, пж,пж\)*\.
8\) Ебни анекдот
  A: Был такой легендарный мужик, который в 20\-е годы написал письмо в ЧЭМК\. Написал он примерно следующее: "Я уже 3 года считаю таблицы с расписанием у вас на сайте \- их то 2, то 3, то 4, а иногда и 1\. Вы там сумасшедшие что ли все?\"
  """, parse_mode='MarkdownV2'))


def create_task(task):
    asyncio.create_task(task)


@bot.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/FAQ", "/Today", "/Tomorrow", "/Subscribe"]
    keyboard.add(*buttons)
    asyncio.create_task(dump_logs(
        f"Issued \"start\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, """Disclaimer: Данный бот не выдает истины последней инстанции, вся информация выданная ботом предоставляется на условиях \"как есть\" без каких-либо гарантий полноты, точности. Не заменяет просмотр расписания на сайте, а также не является официальным проектом связанным с какой-либо оргранизацией с аббревиатурой ЧЭМК.
Бот все еще находится стадии очень ранней разработки. Поэтому могут быть случайные сообщения и некоторые неточности.
Если вы знаете что можно поправить, то пишите.
Другие группы помимо Ир1-20 не поддерживает...
Аптайм бота очень зависит от моего настроения и поэтому бот может быть не всегда доступен 24/7 :)""", reply_markup=keyboard)


@bot.message_handler(commands=["Subscribe", "subscribe"])
async def cmd_start(message: types.Message):
    asyncio.create_task(dump_logs(
        f"Issued \"Today\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    subscribe(message)


def subscribe(message):
    chat_id = message.chat.id
    if not os.path.isfile("config.json"):
        open("config.json", "x").close()
    with open("config.json", "r") as config:
        file_not_empty = os.stat("config.json").st_size > 0
        if file_not_empty:
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
                config.write(json1)
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


async def fast_checker():
    print("Тестовый поиск расписания запущен")
    resp = checker()
    with open("config.json", "r") as config:
        ids = json.loads(config.read())
        print(ids[0]["id"])
        for people_id in ids[0]["id"]:
            create_task(dispatch(people_id, resp))


@bot.message_handler(commands=["test", "Test"])
async def cmd_start(message: types.Message):
    if message.chat.id in allowed_ids:
        create_task(fast_checker())
    else:
        await bot.reply_to(message, "Неа, тебе не разрешено")


@bot.message_handler(commands=["Today", "today"])
async def today(message: types.Message):
    rasp = today_rasp()
    asyncio.create_task(dump_logs(
        f"Issued \"Today\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, rasp)


@bot.message_handler(commands=["Tomorrow", "tomorrow"])
async def tommorrow(message: types.Message):
    rasp = tomorrow_rasp()
    asyncio.create_task(dump_logs(
        f"Issued \"Tomorrow\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, rasp)


@bot.message_handler(func=lambda message: True)
async def unknown_command(message):
    await bot.reply_to(message, "Я не нашел такую команду...")
    await bot.send_animation(message.chat.id, r'https://cdn.discordapp.com/attachments/878333995908222989/1019257151916625930/not_found.gif')


async def invalidate_cache():
    while(True):
        nextday = ((datetime.datetime.now().replace(hour=0, minute=0, second=0) +
                   datetime.timedelta(1)) - datetime.datetime.now()).total_seconds()
        await wait(nextday)
        tomorrow_rasp.cache_clear()
        today_rasp.cache_clear()


async def init():
    create_task(inf_pooling())
    print("Я запустился")
    create_task(invalidate_cache())
    await asyncio.create_task(waiter_checker())


async def inf_pooling():
    while(True):
        try:
            await bot.polling(none_stop=True, timeout=30)
        except Exception as e:
            await dump_logs(f"\nException created: {e}")


if __name__ == "__main__":
    asyncio.run(init())
