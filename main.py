import asyncio
import datetime
import json
import os
from cachetools import cached, TTLCache

import pandas as pd
import requests
from pytils.dt import distance_of_time_in_words
from subprocess import check_output
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import types, asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.formatting import escape_html
from telebot.util import quick_markup

# region disable some rules in pylint
# pylint: disable=anomalous-backslash-in-string, line-too-long, bare-except, missing-function-docstring, unspecified-encoding, broad-except
# endregion

# region some needed vars
load_dotenv("Env/Tokens.env")
token = os.getenv('TOKEN')
groups = os.getenv('GROUP')
name_of_group = os.getenv('NAME_OF_GROUP')
allowed_ids = list(map(int, os.getenv('ALLOWED_IDS').split(',')))
hour_when_start_checking = int(os.getenv('START_HOUR'))
bot = AsyncTeleBot(token)
TODAY = TOMORROW = None
weekday = ["Понедельник", "Вторник", "Среду", "Четверг", "Пятницу", "Субботу"]
month = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
         "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
start_time = datetime.datetime.now()
add_message = ""
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
        if (len(plain_raspisanie[para]) != 0):
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
    print("Я не кэширован!")
    if datetime.datetime.today().strftime('%A') == "Sunday" and day == "Today":
        return "Сегодня Воскресенье, какое раписание на сегодня?\nЧтобы узнать расписание на завтра используй /Tomorrow "
    contents = get_from_site(day)
    if contents is None:
        return "На сайте пока что нет расписания :("
    para = []
    has_group = False
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
    if (has_group):
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
    kab = None
    if len(tables) > 1:  # выстрелит в колено если опять начнется мракобесие с таблицами
        for index in range(len(tables[1])):
            group = tables[1][0][index]
            if group == name_of_group:
                has_group = True
                paras = tables[1][2][index]
                if (paras == "По расписанию"):
                    for nomer in (tables[1][1][index]).split(','):
                        nomer = int(nomer) - 1
                        kab = tables[1][3][index] if len(
                            tables[0].columns) > 3 else None
                        if kab != kab:
                            para.append(
                                f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        else:
                            para.append(
                                f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} {'Кабинет: 'if kab is not None else ''}{kab if kab is not None else ''}")
                elif (paras == "Нет"):
                    para.append(
                        f"Номер пары: {tables[1][1][index]}  Пара: отменена")
                else:
                    para.append(
                        f"Номер пары: {tables[1][1][index]}  Пара: {tables[1][2][index]}  {'Кабинет: 'if kab is not None else ''}{kab if kab is not None else ''}")
            elif group == (name_of_group + " 1 п/г") or group == (name_of_group + " 2 п/г"):
                has_group = True
                paras = tables[1][2][index]
                if (paras.lower() == "по расписанию"):
                    for nomer in (tables[1][1][index]).split(','):
                        nomer = int(nomer) - 1
                        kab = tables[1][3][index] if len(
                            tables[0].columns) > 3 else None
                        if kab != kab:
                            para.append(
                                f"Для {group[6:]} Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        else:
                            para.append(
                                f"Для {group[6:]}Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} {'Кабинет: 'if kab is not None else ''}{kab if kab is not None else ''}")
                elif (paras.lower() == "нет"):
                    para.append(
                        f"Номер пары: {tables[1][1][index]}  Пара: отменена")
                else:
                    para.append(
                        f"Номер пары: {tables[1][1][index]}  Пара: {tables[1][2][index]}  {'Кабинет: 'if kab is not None else ''}{kab if kab is not None else ''}")
    else:
        for index in range(len(tables[0])):
            group = tables[0][0][index]
            kab = tables[0][3][index] if len(tables[0].columns) > 3 else None
            if group == name_of_group:
                has_group = True
                paras = tables[0][2][index]
                if (paras != paras): continue
                if (paras.lower() == "день самостоятельной работы"):
                    para.append(
                        f"День самостоятельной работы")
                elif (paras.lower() == "по расписанию"):
                    for nomer in (tables[0][1][index]).split(','):
                        nomer = int(nomer) - 1
                        if kab != kab:
                            para.append(
                                f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        else:
                            para.append(
                                f"Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} {'Кабинет: 'if kab is not None else ''}{kab if kab is not None else ''}")
                elif (paras.lower() == "нет"):
                    para.append(
                        f"Номер пары: {tables[0][1][index]}  Пара: отменена")
                else:
                    para.append(
                        f"Номер пары: {tables[0][1][index]}  Пара: {tables[0][2][index]}  {'Кабинет: 'if kab is not None else ''}{kab if kab is not None else ''}")
            elif group == (name_of_group + "  1 п/г") or group == (name_of_group + "  2 п/г"):
                has_group = True
                paras = tables[0][2][index]
                kab = tables[0][3][index] if len(
                    tables[0].columns) > 3 else None
                if (paras == "По расписанию"):
                    for nomer in (tables[0][1][index]).split(','):
                        nomer = int(nomer) - 1
                        if kab != kab:
                            para.append(
                                f"Для {group[8:]} Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} Кабинет: {plain_raspisanie[nomer][2]}")
                        else:
                            para.append(
                                f"Для {group[8:]}Номер пары: {nomer+1}  Пара: {plain_raspisanie[nomer][0]}, {plain_raspisanie[nomer][1]} {'Кабинет: 'if kab is not None else ''}{kab if kab is not None else ''}")
                elif (paras == "Нет"):
                    para.append(
                        f"Для {group[8:]} Номер пары: {tables[0][1][index]}  Пара: отменена")
                else:
                    para.append(
                        f"Для {group[8:]} Номер пары: {tables[0][1][index]}  Пара: {tables[0][2][index]}  {'Кабинет: 'if kab is not None else ''}{kab if kab is not None else ''}")

    try:
        para.sort(key=lambda x: int(x.split(":")[1][1].strip()))
    except:
        create_task(dump_logs("Can't sort rasp"))
        
    return has_group


def get_from_site(day):
    responce = requests.get(f"https://rsp.chemk.org/4korp/{day}.htm")
    responce.encoding = 'windows-1251'
    contents = responce.text
    soup = BeautifulSoup(contents, "html.parser")
    schedule_on_site = not (soup.find("div", class_="Section1"))
    if schedule_on_site:
        return contents
    return None


def gen_message(para):
    itogo = ('\n'.join(para))
    return escape_html(itogo)


async def waiter_checker():
    print("Поиск расписания запущен")
    while (True):
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
        while (resp is None):
            resp = checker()
            if resp is None:
                await wait(300)
        with open("config.json", "r") as config:
            ids = json.loads(config.read())
            print(ids[0]["id"])
            for people_id in ids[0]["id"]:
                create_task(dispatcher(people_id, resp))


async def dump_logs(logging_info):
    print("Writted to logs")
    with open("plain_logging.log", "a", encoding="utf-8") as log:
        log.write(logging_info)


def checker():
    print("Чекаю расписание")

    try:
        contents = get_from_site("tomorrow")
        if contents is None:
            return None
        tables = pd.read_html(contents, thousands=None)
        para = []
        has_group = False
        plain_raspisanie = plain_rasp(
            (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%A'))
        has_group = parsing_lines_to_schedule(para, plain_raspisanie, tables)
        if (has_group):
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
    return add_daily_message_to_itogo(itogo)


def add_daily_message_to_itogo(itogo):
    global add_message
    itogo = itogo + "\n\n" + add_message if add_message != '' else itogo
    add_message = ''
    return itogo


async def dispatcher(chat_id, rasp):
    try:
        await bot.send_message(chat_id, rasp, parse_mode='HTML')
    except Exception as e:
        create_task(dump_logs(
            f"I failed to send a message to a user with id {chat_id} because {e}\n"))
        await delete_from_dispatch(chat_id)


# region Temporary code borrowing for a quick fix
async def read_json(name):
    if not os.path.exists(name):
        with open(name, "x", encoding="utf-8"):
            pass
        return None
    with open(name, "r", encoding="utf-8") as f:
        return json.load(f)


async def write_data(name, data):
    if not os.path.exists(name):
        with open(name, "x", encoding="utf-8"):
            pass
    with open(name, "w", encoding="utf-8") as f:
        f.write(data)


async def delete_from_dispatch(id_to_delete):
    ids = await read_json("config.json")
    if id_to_delete in ids[0]["id"]:
        ids[0]["id"].remove(id_to_delete)
    create_task(write_data("config.json", json.dumps(ids, ensure_ascii=False)))
    create_task(dump_logs(f"Deleted {id_to_delete}\n"))
# endregion


async def wait(time):
    print(f"Current time: {datetime.datetime.now()} Sleep time: {datetime.timedelta(seconds=time)}   Sleep until: {datetime.datetime.fromtimestamp(datetime.datetime.timestamp(datetime.datetime.now())+time)}")
    return await asyncio.sleep(time)


@bot.message_handler(commands=["FAQ", "faq"])
async def FAQ(message: types.Message):
    create_task(dump_logs(
        f"Issued \"FAQ\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, """FAQ:
1\)Q: Ну так что там с обработкой данных?
  A: Мы хотим сообщить вам, что наш Telegram\-бот собирает ограниченное количество информации о вас, например, твой ник, твой ID, chat ID и текст сообщений, исключительно для целей логгинга и подписки на нашу ежедневную рассылку\.
Мы не будем использовать информацию в каких\-либо таргетированных/персонализированных рекламных целях\. Будьте уверены, что мы очень серьезно относимся к конфиденциальности и безопасности ваших данных, и никогда не передадим вашу информацию третьим лицам\.
Используя нашего бота, вы соглашаетесь на сбор и использование ваших данных в соответствии с нашей политикой конфиденциальности\. Если у вас возникнут вопросы или проблемы, пожалуйста, обращайтесь к нам\.
2\)Q: Почему бот такой кривой?
  A: Потому что, да
3\)Q: Поддержка других групп?
  A: Поддержка других групп появится в боте v2\.0 \(работы в этом направлении уже ведутся, stay tuned \(вся свежая информация в нашем дискорд сервере https://discord\.gg/YVrasmddPv\)\)\.
4\)Q: Поддержка других корпусов?
  A: Скорее нет, чем да, поддержка других корпусов потребует большого количества работы и скорее всего не будет реализована\.
5\)Q: Сколько будет работать этот бот?
  A: Да\.
6\)Q: Где код?
  A: https://github\.com/SatSea/Chemk\-Rasp\-Parser\-To\-Telegram
7\)Q: Кто принимал участие в создании бота?
  A: /About
8\)Q: Запости кота
  A: /cat
9\)Q: Как можно помочь нам?
  A: Написать о том, что вы бы хотели поменять/исправить \(Нам тяжеловать за всем уследить\)
10\)Q: Может быть хватит добавлять смешнявки/кринж?
  A: Nein\.
11\)Q: Ну че, когда обновы?
  A: Когда\-нибудь
12\)Q: Опять бот не перезапущен после обнов?
  A: Возможно опять с этим проебались, чтобы узнать хэш коммита используй /status и если он не совпадает с тем, что на гитхабе, то мы прооебались, извините\. Мы 🐌\.
13\)Q: Что за ебан писал этот код?
  A: Мы ебаны и мы этмим гордимся\.
14\)Q: А че всмысле, почему в 2 часа ночи бот не доступен?\!??\!?
  A: Kys\.
  """, parse_mode='MarkdownV2')
    create_task(bot.send_animation(
        message.chat.id, 'https://tenor.com/view/tired-groggy-sleepy-what-dazed-gif-16582493918036962522'))


async def cat_pic(chat_id):
    cat = json.loads(requests.get("https://meow.senither.com/v1/random").text)
    if cat['data']['type'] == 'mp4':
        create_task(bot.send_animation(chat_id, cat['data']['url']))
    else:
        create_task(bot.send_photo(chat_id, cat['data']['url']))


@bot.message_handler(commands=["Status", "status"])
async def tommorrow(message: types.Message):
    create_task(dump_logs(
        f"Issued \"Status\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    commit = check_output(['git', 'rev-parse', '--short',
                          'HEAD']).decode('ascii').strip()
    await bot.reply_to(message, f"""Бот запущен {distance_of_time_in_words(start_time, accuracy=3)}
Работает на версии: [{commit}](https://github.com/SatSea/Chemk-Rasp-Parser-To-Telegram/commit/{commit})
Кэш:
    на сегодня: {"Существует" if today_rasp.cache.currsize > 0 else "Инвалидирован"}
    на завтра: {"Существует" if tomorrow_rasp.cache.currsize > 0 else "Инвалидирован"}
""", parse_mode='MarkdownV2')
    create_task(bot.send_animation(message.chat.id,
                'https://tenor.com/view/status-report-status-update-kowalski-status-report-kowalski-status-gif-23668188'))


@bot.message_handler(commands=["Cat", "cat"])
async def cat(message: types.Message):
    create_task(dump_logs(
        f"Issued \"Cat\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    create_task(cat_pic(message.chat.id))


@bot.message_handler(commands=["About", "about"])
async def tommorrow(message: types.Message):
    create_task(dump_logs(
        f"Issued \"About\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(
        message, """Прямое участие в разработке принимали: Satsea(aka Aestas) [Код и изначальная идея], SashaGHT(aka Lysk) [Немного будущего кода (для поддержки нескольких групп), редактура текста и бóльшая часть написанного текста], ALLAn [помощь в распутывании и расчесывании спагетти-кода]
Косвенное участие в разработке: Ania [Донаты на печеньки и пиво, и (м)оральная поддержка!], SuriCafe[твои донаты пошли точно не на пиво и спасибо за моральную поддержку!!!]""")
    create_task(bot.send_animation(message.chat.id,
                'https://tenor.com/view/cat-bread-kitten-kitty-cute-gif-17858209'))


def create_task(task):
    asyncio.create_task(task)


@bot.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/FAQ", "/Today", "/Tomorrow", "/Subscribe", "/Schedule"]
    keyboard.add(*buttons)
    create_task(dump_logs(
        f"Issued \"start\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, """Disclaimer: Мы собираем ограниченное количество информации о вас, например, твой ник, твой ID, chat ID и текст сообщений, исключительно для целей логгинга и подписки на нашу ежедневную рассылку. Мы не будем использовать информацию в каких-либо таргетированных/персонализированных рекламных целях. Будьте уверены, что мы очень серьезно относимся к конфиденциальности и безопасности ваших данных, и никогда не передадим вашу информацию третьим лицам.
Данный бот не выдает истины последней инстанции, вся информация выданная ботом предоставляется на условиях \"как есть\" без каких-либо гарантий полноты, точности. Не заменяет просмотр расписания на сайте, а также не является официальным проектом связанным с какой-либо организацией с аббревиатурой ЧЭМК.
Бот все еще находится стадии очень ранней разработки. Поэтому могут быть случайные сообщения и некоторые неточности.
Другие группы помимо Ир1-20 пока что не поддерживает...
Аптайм бота очень зависит от настроения и поэтому бот может быть не всегда доступен 24/7 :)
Используя нашего бота, вы соглашаетесь на сбор и использование ваших данных в соответствии с нашей политикой конфиденциальности. Если у вас возникнут вопросы или проблемы, пожалуйста, обращайтесь к нам.""", reply_markup=keyboard)


@bot.message_handler(commands=["Subscribe", "subscribe"])
async def cmd_start(message: types.Message):
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
                if (chat_id in ids):
                    try:
                        ids.remove(chat_id)
                    except:
                        create_task(bot.reply_to(
                            message, "Не получилось отписаться от обновлений расписания"))
                    else:
                        create_task(dump_logs(
                            f"Issued \"Subscribe\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] to unsubscribe from everyday mailing in {datetime.datetime.fromtimestamp(message.date)}\n"))
                        create_task(bot.reply_to(
                            message, "Успешно получилось отписаться от обновлений расписания"))
                        create_task(bot.send_animation(
                            message.chat.id, 'https://i.gifer.com/3jRk.gif'))
                else:
                    ids.append(chat_id)
                    create_task(dump_logs(
                        f"Issued \"Subscribe\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] to subscribe to the everyday mailing in {datetime.datetime.fromtimestamp(message.date)}\n"))
                    create_task(bot.reply_to(
                        message, "Успешно подписан на обновления расписания"))
                    create_task(bot.send_animation(
                        message.chat.id, 'https://tenor.com/view/at-your-service-sir-kif-zapp-brannigan-futurama-here-to-help-gif-5917278640134074942'))
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
                    create_task(dump_logs(
                        f"Issued \"Subscribe\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] subscribe to the everyday mailing in {datetime.datetime.fromtimestamp(message.date)}\n"))

                    create_task(bot.reply_to(
                        message, "Успешно подписан на обновление расписания"))
                    create_task(bot.send_animation(
                        message.chat.id, 'https://tenor.com/view/at-your-service-sir-kif-zapp-brannigan-futurama-here-to-help-gif-5917278640134074942'))
                except:
                    config.write(json1)
                    create_task(dump_logs(
                        f"Issued \"Subscribe\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] subscribe to the everyday mailing in {datetime.datetime.fromtimestamp(message.date)}\n"))
                    create_task(bot.reply_to(
                        message, "Успешно подписан на обновление расписания"))
                    create_task(bot.send_animation(
                        message.chat.id, 'https://tenor.com/view/at-your-service-sir-kif-zapp-brannigan-futurama-here-to-help-gif-5917278640134074942'))


async def fast_checker():
    print("Тестовый поиск расписания запущен")
    resp = checker()
    with open("config.json", "r") as config:
        ids = json.loads(config.read())
        print(ids[0]["id"])
        for people_id in ids[0]["id"]:
            create_task(dispatcher(people_id, resp))


@bot.message_handler(commands=["Dispatch", "dispatch"])
async def dispatch(message: types.Message):
    create_task(dump_logs(
        f"Issued \"Dispatch\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    if message.chat.id in allowed_ids:
        await bot.reply_to(message, "Джин выпущен из бутылки")
        create_task(fast_checker())
    else:
        await bot.reply_to(message, "Неа, тебе не разрешено")
        create_task(bot.send_animation(
            message.chat.id, 'https://tenor.com/view/among-us-twerk-yellow-ass-thang-gif-18983570'))


@bot.message_handler(commands=["Add_daily_message", "add_daily_message"])
async def daily_message(message: types.Message):
    create_task(dump_logs(
        f"Issued \"Dispatch\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    if message.chat.id not in allowed_ids:
        await bot.reply_to(message, "Неа, тебе не разрешено")
        create_task(bot.send_animation(message.chat.id,
                                       'https://tenor.com/view/among-us-twerk-yellow-ass-thang-gif-18983570'))
        return
    await bot.reply_to(message, "Яви свое послание народу")
    create_task(bot.set_state(message.from_user.id,
                "add_message", message.chat.id))


@bot.message_handler(state="add_message")
async def add_daily_message(message: types.Message):
    if message.chat.id not in allowed_ids:
        await bot.reply_to(message, "Неа, тебе не разрешено")
        create_task(bot.send_animation(
            message.chat.id, 'https://tenor.com/view/lord-of-the-rings-lotr-theoden-rohan-two-towers-gif-13863406401517703527'))
        return
    global add_message
    add_message = f"{message.html_text}\nСообщение от: @{message.from_user.username}"
    await bot.reply_to(
        message, "Добавлю к следующей рассылке данный текст:\n" + add_message, parse_mode='HTML')
    create_task(dump_logs(
        f"Added to Daily_message \"{add_message}\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    create_task(bot.delete_state(message.from_user.id, message.chat.id))


@bot.message_handler(commands=["Daily_message", "daily_message"])
async def daily_message(message: types.Message):
    if message.chat.id not in allowed_ids:
        create_task(bot.reply_to(message, "Неа, тебе не разрешено"))
        create_task(bot.send_animation(
            message.chat.id, 'https://tenor.com/view/lord-of-the-rings-lotr-theoden-rohan-two-towers-gif-13863406401517703527'))
        return
    create_task(dump_logs(
        f"Issued \"Daily_message\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    if (add_message == ''):
        return create_task(bot.reply_to(message, "Мне нечего добавлять к ежедневной рассылке"))
    create_task(bot.reply_to(
        message, "Я дополню ежедневную рассылку этим:\n" + add_message, parse_mode='HTML'))


@bot.message_handler(commands=["Send_message", "send_message"])
async def Send_message(message: types.Message):
    global add_message
    if message.chat.id not in allowed_ids:
        await bot.reply_to(message, "Неа, тебе не разрешено")
        create_task(bot.send_animation(
            message.chat.id, 'https://tenor.com/view/lord-of-the-rings-lotr-theoden-rohan-two-towers-gif-13863406401517703527'))
        return
    create_task(dump_logs(
        f"Issued \"Send_message\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    if (add_message == ''):
        return create_task(bot.reply_to(message, "В рассылке ничего нет"))
    with open("config.json", "r") as config:
        ids = json.loads(config.read())
        print(ids[0]["id"])
        for people_id in ids[0]["id"]:
            create_task(dispatcher(people_id, add_message))
    add_message = ''


@bot.message_handler(commands=["Clear_daily_message", "clear_daily_message"])
async def clear_daily_message(message: types.Message):
    global add_message
    if message.chat.id not in allowed_ids:
        await bot.reply_to(message, "Неа, тебе не разрешено")
        create_task(bot.send_animation(
            message.chat.id, 'https://tenor.com/view/among-us-twerk-yellow-ass-thang-gif-18983570'))
        return
    create_task(dump_logs(
        f"Issued \"Clear_daily_message\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    if (add_message == ''):
        return create_task(bot.reply_to(message, "Мне нечего удалять"))
    add_message = ''
    create_task(bot.reply_to(
        message, "Успешно удалил дополнительный текст к ежедневной рассылке"))


@bot.message_handler(commands=["Today", "today"])
async def today(message: types.Message):
    rasp = today_rasp()
    create_task(dump_logs(
        f"Issued \"Today\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, rasp, parse_mode='HTML')


@bot.message_handler(commands=["Tomorrow", "tomorrow"])
async def tommorrow(message: types.Message):
    rasp = tomorrow_rasp()
    create_task(dump_logs(
        f"Issued \"Tomorrow\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, rasp, parse_mode='HTML')


@bot.message_handler(commands=["Schedule", "schedule"])
async def Schedule(message: types.Message):
    create_task(dump_logs(
        f"Issued \"Schedule\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] in {datetime.datetime.fromtimestamp(message.date)}\n"))

    markup = quick_markup({
        'На завтра': {'callback_data': 'tomorrow'}
    })

    create_task(bot.reply_to(message, get_schedule(
        "today"), reply_markup=markup))


def get_schedule(day: str):
    day_of_week = (datetime.datetime.today().isoweekday() +
                   (1 if day == "tomorrow" else 0)) % 8 or 1

    match(day_of_week):
        case 1:
            schedule = "Расписание звонков на понедельник:\n\n1 пара: 8:15 – 9:00 9:10 – 9:55 \n2 пара: 10:05 – 10:55 11:25 – 12:05 \nКлассный час: 12:15 – 12:45 \n3 пара: 12:55 – 13:40 13:50 – 14:35 \n4 пара: 14:45 – 15:30 15:40 – 16:25 \n5 пара: 16:35 – 17:20 17:30 – 18:15 \n6 пара: 18:25 – 19:10 19:15 – 20:00"
        case 7:
            schedule = "Расписание звонков на воскресенье:\n\nПить пиво"
        case _:
            schedule = f"Расписание звонков на {weekday[day_of_week - 1].lower()}:\n\n1 пара: 8:15 – 9:00 9:10 – 9:55 \n2 пара: 10:05 – 10:55 11:25 – 12:05 \n3 пара: 12:15 – 13:00 13:10 – 13:55 \n4 пара: 14:15 – 15:00 15:10 – 15:55 \n5 пара: 16:05 – 16:50 17:00 – 17:45 \n6 пара: 17:55 – 18:40 18:50 – 19:35"
    return schedule


@bot.callback_query_handler(func=lambda call: call.data == "tomorrow")
async def schedule_change_to_today_handler(callback_query: types.CallbackQuery):
    message = callback_query.message
    create_task(dump_logs(
        f"Changed schedule from today to tomorrow by {callback_query.from_user.username} ({callback_query.from_user.full_name}) [{callback_query.from_user.id}] in {datetime.datetime.now()}\n"))

    markup = quick_markup({
        'На сегодня': {'callback_data': 'today'}
    })
    await (bot.edit_message_text(get_schedule("tomorrow"), message.chat.id,
                                 message.message_id, reply_markup=markup))
    create_task(bot.answer_callback_query(callback_query.id))


@bot.callback_query_handler(func=lambda call: call.data == "today")
async def schedule_change_to_tomorrow_handler(callback_query: types.CallbackQuery):
    message = callback_query.message
    create_task(dump_logs(
        f"Changed schedule from tomorrow to today by {callback_query.from_user.username} ({callback_query.from_user.full_name}) [{callback_query.from_user.id}] in {datetime.datetime.now()}\n"))

    markup = quick_markup({
        'На завтра': {'callback_data': 'tomorrow'}
    })
    await (bot.edit_message_text(get_schedule("today"), callback_query.message.chat.id,
                                 callback_query.message.message_id, reply_markup=markup))
    create_task(bot.answer_callback_query(callback_query.id))


@bot.message_handler(func=lambda message: True)
async def unknown_command(message):
    await bot.reply_to(message, "Я не нашел такую команду...")
    create_task(dump_logs(
        f"{message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] wrote \"{message.text}\", but I did not understand what he wrote at in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.send_animation(message.chat.id, 'https://tenor.com/view/raccoon-cute-cotton-candy-wash-dissolve-gif-17832451')


async def invalidate_cache():
    while (True):
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
    while (True):
        try:
            await bot.polling(none_stop=True, timeout=30)
        except Exception as e:
            await dump_logs(f"\nException created: {e}")

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

if __name__ == "__main__":
    asyncio.run(init())
