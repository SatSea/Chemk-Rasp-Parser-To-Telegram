from subprocess import check_output
from aiogram import types, Dispatcher
from init_bot import dp
from keyboard import regular_kb
from pytils.dt import distance_of_time_in_words
from misc import create_task, cat_pic
from main import start_time
from log import logger
from parse import group_today_rasp, group_tommorrow_rasp

# @dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = [
    "/FAQ",
    "/Today",
    "/Tomorrow",
    "/Subscribe"
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*kb)
    logger.info(
        f"Issued \"start\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    create_task(message.reply("""Disclaimer: Бот не выдает истины последней инстанции, вся информация предоставляется на условиях \"как есть\" без каких-либо гарантий полноты, точности. Не заменяет просмотр расписания на сайте, а также не является чьим-либо официальным проектом.
Проект все еще находится стадии очень ранней разработки, поэтому могут быть неточности и многие другие прелести неотлаженного кода.
Если вы знаете что можно поправить, то пишите.
Другие группы помимо Ир1-20 пока что не поддерживает...
Аптайм бота очень зависит от моего настроения и поэтому бот может быть не всегда доступен 24/7 :)""", reply_markup=keyboard))

# @dp.message_handler(commands=["FAQ", "faq"])
async def faq(message: types.Message):
    logger.info(
        f"Issued \"FAQ\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    create_task(message.answer("""FAQ:
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
  """, parse_mode='MarkdownV2'))

@dp.message_handler(commands=["Status", "status"])
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
    create_task(message.answer_animation(
                'https://cdn.discordapp.com/attachments/878333995908222989/1048634370031882310/homer-simpson.gif'))

# @dp.message_handler(commands=["Cat", "cat"])
async def cat(message: types.Message):
    logger.info(
        f"Issued \"Cat\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    pic, type = await cat_pic()
    if type == 'mp4':
        create_task(message.reply_animation(pic))
    else:
        create_task(message.reply_photo(pic))

# @dp.message_handler(commands=["About", "about"])
async def about(message: types.Message):
    logger.info(
        f"Issued \"About\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    create_task(message.reply(
        "Участие в разработке принимали: Satsea(aka Aestas) [Код и изначальная идея], SashaGHT(aka Lysk) [Немного будущего кода (для поддержки нескольких групп), редактура текста и бóльшая часть написанного текста], ALLAn [помощь в распутывании и расчесывании спагетти-кода]\nКосвенная помощь в разработке: Ania [Донаты на печеньки и пиво, и моральная поддержка!]"))
    create_task(message.answer_animation(
                'https://cdn.discordapp.com/attachments/878333995908222989/1032677359926653008/sleepy-at-work-sleepy-kitten.gif'))

# @dp.message_handler(commands=["Today", "today"])
async def today(message: types.Message):
    try:
        rasp = await group_today_rasp()
        create_task(message.reply(rasp))
        logger.info(
            f"Issued \"Today\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    except Exception as e:
        logger.exception(
            f"{message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] issued \"Today\", but I couldn't make and send a rasp")
        create_task(message.reply("У меня не получилось получить расписание на сегодня"))


# @dp.message_handler(commands=["Tomorrow", "tomorrow"])
async def tommorrow(message: types.Message):
    try:
        rasp = await group_tommorrow_rasp()
        create_task(message.reply(rasp))
        logger.info(
            f"Issued \"Tomorrow\" from {message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}]")
    except Exception as e:
        logger.exception(
            f"{message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] issued \"Today\", but I couldn't make and send a rasp")
        create_task(message.reply("У меня не получилось получить расписание на завтра"))



# @dp.message_handler()
async def unknown_commnand(message: types.Message):
    create_task(message.reply('Я не нашел такую команду...'))
    create_task(message.answer_animation('https://cdn.discordapp.com/attachments/878333995908222989/1019257151916625930/not_found.gif'))
    logger.warning(f"{message.from_user.username} ({message.from_user.full_name}) [{message.from_user.id}] wrote \"{message.text}\", but I did not understand what he wrote")

async def register_regular_handlers(dp : Dispatcher):
    dp.register_message_handler(about, commands=["About", "about"])
    dp.register_message_handler(cat, commands=["Cat", "cat"])
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(status, commands=["Status", "status"])
    dp.register_message_handler(faq, commands=["FAQ", "faq"])
    dp.register_message_handler(today, commands=["Today", "today"])
    dp.register_message_handler(tommorrow, commands=["Tomorrow", "tomorrow"])
    dp.register_message_handler(unknown_commnand)
    