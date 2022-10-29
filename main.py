import asyncio
import datetime
import json
from cachetools import cached, TTLCache

import pandas as pd
import requests
from bs4 import BeautifulSoup
from os import getenv, path
from dotenv import load_dotenv
from telebot import types
from telebot.async_telebot import AsyncTeleBot

# region disable some rules in pylint
# pylint: disable=anomalous-backslash-in-string, line-too-long, bare-except, missing-function-docstring, unspecified-encoding, broad-except
# endregion

# region some needed vars
load_dotenv("Env/Tokens.env")
token = getenv('TOKEN')
groups = getenv('GROUP')
name_of_group = getenv('NAME_OF_GROUP')
allowed_ids = list(map(int, getenv('ALLOWED_IDS').split(',')))
hour_when_start_checking = int(getenv('START_HOUR'))
bot = AsyncTeleBot(token)
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


def get_plain_rasp(name, day):
    return "nomer", "para", "kab"


# I am very embarrassed about this code
def parsing_lines_to_schedule(para, plain_raspisanie, tables):
    """
    I am very ashamed of this code, someone will need to rewrite it ASAP.
    """
    paras = {}
    itog = {}
    for i, cell in enumerate(tables[0][2]):
        name_of_group = tables[0][0][i]
        if name_of_group == name_of_group:
            name_without_subgroup = name_of_group[:6]
            if type(name_of_group) is str and len(name_of_group) <= 13 and name_of_group != "Группа":
                if name_without_subgroup not in paras:
                    paras[name_without_subgroup] = []
                test = name_of_group[-3:]
                if cell == "По расписанию":
                    tomorrow = (datetime.datetime.today() +
                                datetime.timedelta(days=1)).strftime('%A')
                    nomer, para, kab = plain_raspisanie[name_without_subgroup][tomorrow]
                else:
                    nomer, para, kab = tables[0][1][i], cell, tables[0][3][i]
                if name_of_group[-3:] == "п/г":
                    rasp = f"Для {name_of_group[-5:]} Номер {nomer} Пара {para} Кабинет {kab}" if cell != "Нет" else f"Для {name_of_group[-5:]} Номер {nomer} Пара {para}"
                    paras[name_without_subgroup].append(rasp)
                else:
                    rasp = f"Номер пары {nomer} Пара {para} Кабинет {kab}" if cell != "Нет" else f"Номер пары {nomer} Пара {para}"
                    paras[name_without_subgroup].append(rasp)
    for name, pari in paras.items():
        itog[name] = "\n".join(pari)
    return itog


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
        contents = get_from_site("tomorrow")
        if contents is None:
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
    asyncio.create_task(dump_logs(
        f"Issued \"FAQ\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    create_task(bot.reply_to(message, """FAQ: 
1\)Q: Почему бот такой кривой?
  A: Потому что, бюджета не хватило даже на банку пива и разрабатывало все это долбоеб\(ка\) на разработке
2\)Q: Поддержка других групп?
  A: Когда\-нибудь поддержка других групп появится \(работы в этом направлении уже ведутся, stay tuned\(вся свежая информация в нашем дискорд сервере \{discord\_url\}\)\)\.
3\)Q: Поддержка других корпусов?
  A: Скорее нет, чем да, поддержка других корпусов потребует большого количества работы и скорее всего не будет реализована\.
4\)Q: Сколько будет работать этот бот?
  A: Да\.
5\)Q: Код будет выложен?
  A: https://github\.com/SatSea/Chemk\-Rasp\-Parser\-To\-Telegram
6\)Q: Почему бот иногда так долго отвечает?
  A: а\) Все таки одного ядро уже не хватает :\)
б\) Период рассылки сообщений
в\) Опять сайт ЧЭМК ограничил скорость для меня, опять\.\.\.\.
г\) Произошел форс\-мажор \(Поймите и простите\)
~д\) Бот ушел опять в бесконечную петлю~ 
7\)Q: GDPR? \(aka Политика конфиденциальности\)
  A: Да, мы собираем некоторую информацию о пользователях \(Ник, время, исполненная команда, статус выполнения команды\)
  *Но данные удаляются по первому требованию пользователя или по истечению 30 дней*\.
8\) Ебни анекдот
  A: Был такой легендарный мужик, который в 20\-е годы написал письмо в ЧЭМК\. Написал он примерно следующее: "Я уже 3 года считаю таблицы с расписанием у вас на сайте \- их то 2, то 3, то 4, а иногда и 1\. Вы там сумасшедшие что ли все?\"
9\)Q: Кто принимал участие в создании бота?
  A: /About
10\)Q: Сколько часов заняла разработка этого бота?
  A: Порядка 25\-30 часов написания кода, 10 человеко\-часов тестирования
11\)Q: Запости кота
  A: /cat
12\)Q: Как можно помочь проекту?
  A: Написать о том, что вы бы хотели поменять/исправить \(Нам тяжеловать за всем уследить\)
  """, parse_mode='MarkdownV2'))


async def cat_pic(chat_id):
    cat = json.loads(requests.get("https://meow.senither.com/v1/random").text)
    if cat['data']['type'] == 'mp4':
        create_task(bot.send_animation(chat_id, cat['data']['url']))
    else:
        create_task(bot.send_photo(chat_id, cat['data']['url']))


@bot.message_handler(commands=["Cat", "cat"])
async def cat(message: types.Message):
    asyncio.create_task(dump_logs(
        f"Issued \"Cat\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    create_task(cat_pic(message.chat.id))


@bot.message_handler(commands=["About", "about"])
async def tommorrow(message: types.Message):
    asyncio.create_task(dump_logs(
        f"Issued \"About\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    create_task(bot.reply_to(
        message, "Участие в разработке принимали: Satsea(aka Aestas) [Код и изначальная идея] и SashaGHT(aka Lysk) [Немного будущего кода (для поддержки нескольких групп), редактура текста и бóльшая часть написанного текста]"))
    create_task(bot.send_animation(message.chat.id,
                'https://cdn.discordapp.com/attachments/878333995908222989/1032677359926653008/sleepy-at-work-sleepy-kitten.gif'))


def create_task(task):
    asyncio.create_task(task)


@bot.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/FAQ", "/Today", "/Tomorrow", "/Subscribe"]
    keyboard.add(*buttons)
    asyncio.create_task(dump_logs(
        f"Issued \"start\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    await bot.reply_to(message, """Disclaimer: Данный бот не выдает истины последней инстанции, вся информация выданная ботом предоставляется на условиях \"как есть\" без каких-либо гарантий полноты, точности. Не заменяет просмотр расписания на сайте, а также не является официальным проектом связанным с какой-либо организацией с аббревиатурой ЧЭМК.
Бот все еще находится стадии очень ранней разработки. Поэтому могут быть случайные сообщения и некоторые неточности.
Если вы знаете что можно поправить, то пишите.
Другие группы помимо Ир1-20 пока что не поддерживает...
Аптайм бота очень зависит от моего настроения и поэтому бот может быть не всегда доступен 24/7 :)""", reply_markup=keyboard)


@bot.message_handler(commands=["Subscribe", "subscribe"])
async def cmd_start(message: types.Message):
    asyncio.create_task(dump_logs(
        f"Issued \"Subscribe\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    create_task(subscribe(message))


def read_json(name):
    if not path.exists(name):
        with open(name, "x", encoding="utf-8"):
            pass
        return None
    with open(name, "r", encoding="utf-8") as f:
        return json.load(f)


def write_data(name, data):
    if not path.exists(name):
        with open(name, "x", encoding="utf-8"):
            pass
    with open(name, "w", encoding="utf-8") as f:
        f.write(data)


def check_for_id(check_id, group):
    ids = read_json("ids.json")
    if group not in ids:
        ids[group] = []
    if check_id in ids[group]:
        ids[group].remove(check_id)
        is_deleted = True
    else:
        ids[group].append(check_id)
        is_deleted = False
    write_data("ids.json", json.dumps(ids, ensure_ascii=False))
    return is_deleted


async def subscribe(message):
    groups = ["Ит1-22", "Са1-21", "Са3-21", "С1-21", "С3-21", "Ир1-21", "Ир3-21", "Ир5-21", "С1-20", "С3-20", "Ип1-20", "Ип3-20", "Ир1-20", "Ир3-20", "Ир5-20",
              "Кс1-20", "Кс3-20", "Кс5-20", "Ип1-19", "Ип3-19", "Ир1-19", "Ир3-19", "Ир5-19", "Кс1-19", "Кс3-19", "Кс5-19", "С1-19", "С3-19", "С1-18", "С3-18"]
    row = []
    keyboard = []
    i = 0
    for i, button in enumerate(groups):
        row.append(types.InlineKeyboardButton(
            button, callback_data="rasp_"+button))
        if i % 4 == 0:
            keyboard.append(row)
            row = []
    keyboard.append(row)
    reply_markup = types.InlineKeyboardMarkup(keyboard, row_width=16)
    create_task(bot.send_message(message.chat.id,
                "Выбери группу на расписание которой ты хочешь подписаться", reply_markup=reply_markup))


@bot.callback_query_handler(func=lambda call: True)
async def callback_inline(call):
    if call.data[:5] == "rasp_":
        if check_for_id(call.from_user.id, call.data):
            create_task(bot.send_message(
                call.from_user.id, f"Успешно отписался от рассылки расписания для группы {call.data}"))
        else:
            create_task(bot.send_message(
                call.from_user.id, f"Успешно подписался на рассылку расписания для группы {call.data}"))


async def fast_checker():
    print("Тестовый поиск расписания запущен")
    resp = checker()
    with open("config.json", "r") as config:
        ids = json.loads(config.read())
        print(ids[0]["id"])
        for people_id in ids[0]["id"]:
            create_task(dispatch(people_id, resp))


@bot.message_handler(commands=["Test", "test"])
async def cmd_start(message: types.Message):
    create_task(dump_logs(
        f"Issued \"Test\" from {message.from_user.username} in {datetime.datetime.fromtimestamp(message.date)}\n"))
    if message.chat.id in allowed_ids:
        create_task(fast_checker())
    else:
        await bot.reply_to(message, "Неа, тебе не разрешено")
        create_task(bot.send_animation(
            message.chat.id, 'https://cdn.discordapp.com/attachments/878333995908222989/1032669199581073428/you-have-no-power-here.gif'))


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
