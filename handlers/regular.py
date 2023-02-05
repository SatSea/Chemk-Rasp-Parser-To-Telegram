from subprocess import check_output
from aiogram import types, Dispatcher
from aiogram.filters import Command
from init_bot import dp
from datetime import datetime
from keyboard.regular_kb import get_regular_kb
from keyboard.inline_kb import get_inline_sub_kb
from pytils.dt import distance_of_time_in_words
from misc import cat_pic
from main import start_time
from log import logger
from parse import group_rasp

# @dp.message(commands=["start"])
async def start(message: types.Message):
    logger.info(
        f"Issued \"start\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    await message.reply("""Disclaimer: Бот не выдает истины последней инстанции, вся информация предоставляется на условиях \"как есть\" без каких-либо гарантий полноты, точности. Не заменяет просмотр расписания на сайте, а также не является чьим-либо официальным проектом.
Проект все еще находится стадии очень ранней разработки, поэтому могут быть неточности и многие другие прелести неотлаженного кода.
Если вы знаете что можно поправить, то пишите.
Другие группы помимо Ир1-20 пока что не поддерживает...
Аптайм бота очень зависит от моего настроения и поэтому бот может быть не всегда доступен 24/7 :)""", reply_markup=await get_regular_kb())

# @dp.message(commands=["FAQ", "faq"])
async def faq(message: types.Message):
    logger.info(
        f"Issued \"FAQ\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    await message.answer("""FAQ:
1\)Q: Почему бот такой кривой?
  A: Потому что, бюджета не хватило даже на банку пива и разрабатывало все это долбоеб\(ка\) на разработке
2\)Q: Поддержка других групп?
  A: Когда\-нибудь поддержка других групп появится \(работы в этом направлении уже ведутся, stay tuned \(вся свежая информация в нашем дискорд сервере https://discord\.gg/YVrasmddPv\)\)\.
3\)Q: Поддержка других корпусов?
  A: Скорее нет, чем да, поддержка других корпусов потребует большого количества работы и скорее всего не будет реализована\.
4\)Q: Сколько будет работать этот бот?
  A: Да\.
5\)Q: Код будет выложен?
  A: https://github\.com/SatSea/Chemk\-Rasp\-Parser\-To\-Telegram
6\)Q: Ебни анекдот
  A: Был такой легендарный мужик, который в 20\-е годы написал письмо в ЧЭМК\. Написал он примерно следующее: "Я уже 3 года считаю таблицы с расписанием у вас на сайте \- их то 2, то 3, то 4, а иногда и 1\. Вы там сумасшедшие что ли все?\"
8\)Q: Кто принимал участие в создании бота?
  A: /About
9\)Q: Запости кота
  A: /cat
10\)Q: Как можно помочь нам?
  A: Написать о том, что вы бы хотели поменять/исправить \(Нам тяжеловать за всем уследить\)
11\)Q: Может быть хватит добавлять смешнявки/кринж?
  A: Nein
12\)Q: Ну че, когда обновы?
  A: Когда\-нибудь
13\)Q: Опять бот не перезапущен после обнов?
  A: Возможно опять с этим проебались, чтобы узнать хэш коммита используй /status и если он не совпадает с тем, что на гитхабе, то мы прооебались, извините\. Мы 🐌\.
  """, parse_mode='MarkdownV2')

# @dp.message(commands=["Status", "status"])
async def status(message: types.Message):
    logger.info(
        f"Issued \"Status\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    try:
        commit = check_output(['git', 'rev-parse', '--short',
                          'HEAD']).decode('ascii').strip()
    except:
        commit = "Не получилось получить хэш коммита"
    await message.reply(f"""Бот запущен {distance_of_time_in_words(start_time, accuracy=3)}
Работает на версии: [{commit}](https://github.com/SatSea/Chemk-Rasp-Parser-To-Telegram/commit/{commit}) """
# Кеш: на сегодня: {"Существует" if today_rasp.cache.currsize > 0 else "Инвалидирован"}
# на завтра: {"Существует" if tomorrow_rasp.cache.currsize > 0 else "Инвалидирован"}
, parse_mode='MarkdownV2')
    await message.answer_animation(
                'https://cdn.discordapp.com/attachments/878333995908222989/1048634370031882310/homer-simpson.gif')

# @dp.message(commands=["Cat", "cat"])
async def cat(message: types.Message):
    logger.info(
        f"Issued \"Cat\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    pic, type = await cat_pic()
    if type == 'mp4':
        await message.reply_animation(pic)
    else:
        await message.reply_photo(pic)

# @dp.message(commands=["About", "about"])
async def about(message: types.Message):
    logger.info(
        f"Issued \"About\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    await message.reply(
        "Участие в разработке принимали: Satsea(aka Aestas) [Код и изначальная идея], SashaGHT(aka Lysk) [Немного будущего кода (для поддержки нескольких групп), редактура текста и бóльшая часть написанного текста], ALLAn [помощь в распутывании и расчесывании спагетти-кода]\nКосвенная помощь в разработке: Ania [Донаты на печеньки и пиво, и моральная поддержка!]")
    await message.answer_animation(
                'https://cdn.discordapp.com/attachments/878333995908222989/1032677359926653008/sleepy-at-work-sleepy-kitten.gif')

# @dp.message(commands=["Today", "today"])
async def today(message: types.Message):
    try:
        rasp = await group_today_rasp()
        await message.reply(rasp)
        logger.info(
            f"Issued \"Today\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    except Exception as e:
        logger.exception(
            f"{message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] issued \"Today\", but I couldn't make and send a rasp")
        await message.reply("У меня не получилось получить расписание на сегодня")


# @dp.message(commands=["Tomorrow", "tomorrow"])
async def tommorrow(message: types.Message):
    try:
        rasp = await group_tommorrow_rasp()
        await message.reply(rasp)
        logger.info(
            f"Issued \"Tomorrow\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    except Exception as e:
        logger.exception(
            f"{message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] issued \"Today\", but I couldn't make and send a rasp")
        await message.reply("У меня не получилось получить расписание на завтра")

# @dp.message(commands=["Schedule", "schedule"])
async def schedule(message: types.Message):
    match(datetime.today().isoweekday()):
        case 1:
            schedule = "Расписание звонков на понедельник:\n\nИнформационная 5-минутка: 8.10 - 8.15\n1 пара: 8:15 – 9:00 9:10 – 9:55 \n2 пара: 10:05- 10:35 11:05 – 12:05 \n3 пара: 12:15 – 13:00 13:10 – 13:55 \n4 пара: 14:15 – 15:00 15:10 – 15:55 \n5 пара: 16:05 – 16:50 17:00 – 17:45 \n6 пара: 17:55 – 18:40 18:50 – 19:35"
        case 2:
            schedule = "Расписание звонков на вторник:\n\n1 пара: 8:15 – 9:00 9:10 – 9:55 \n2 пара: 10:05- 10:35 11:05 – 12:05 \nКлассный час 12:15 – 12:45 \n3 пара: 12:55 – 13:40 13:50 – 14:35 \n4 пара: 14:45 – 15:30 15:40 – 16:25 \n5 пара: 16:35 – 17:20 17:30 – 18:15 \n6 пара: 18:25 – 19:10 19:15 – 20:00"
        case _:
            schedule = "Расписание звонков:\n\n1 пара: 8:15 – 9:00 9:10 – 9:55 \n2 пара: 10:05- 10:35 11:05 – 12:05 \n3 пара: 12:15 – 13:00 13:10 – 13:55 \n4 пара: 14:15 – 15:00 15:10 – 15:55 \n5 пара: 16:05 – 16:50 17:00 – 17:45 \n6 пара: 17:55 – 18:40 18:50 – 19:35"
    await message.reply(schedule)
    logger.info(
        f"Issued \"Schedule\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")


# @dp.message(commands=["Subscribe", "subscribe"])
async def subscribe(message: types.Message):
    await message.reply("Выбери группы на которые ты хочешь подписаться:", reply_markup=await get_inline_sub_kb(message.from_user.id))
    logger.info(
        f"Issued \"Schedule\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")


# @dp.message()
async def unknown_commnand(message: types.Message):
    await message.reply('Я не нашел такую команду...')
    await message.answer_animation('https://cdn.discordapp.com/attachments/878333995908222989/1019257151916625930/not_found.gif')
    logger.warning(f"{message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] wrote \"{message.text}\", but I did not understand what he wrote")

async def register_regular_handlers(dp : Dispatcher):
    dp.message.register(about, Command(commands=["test"]))
    dp.message.register(cat, Command(commands=["Cat", "cat"]))
    dp.message.register(start, Command(commands=["start"]))
    dp.message.register(status, Command(commands=["Status", "status"]))
    dp.message.register(faq, Command(commands=["FAQ", "faq"]))
    dp.message.register(today, Command(commands=["Today", "today"]))
    dp.message.register(tommorrow, Command(commands=["Tomorrow", "tomorrow"]))
    dp.message.register(schedule, Command(commands=["Schedule", "schedule"]))
    dp.message.register(subscribe, Command(commands=["Subscribe", "subscribe"]))
    dp.message.register(unknown_commnand)
    