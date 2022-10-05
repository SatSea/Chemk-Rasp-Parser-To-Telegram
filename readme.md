<!-- markdownlint-disable MD053 MD040 -->
# CHEMK RASP PARSER TO TELEGRAM

## Проект является заглушкой до появления более нового и качественного легкого способа получить расписание, не стоит использовать его на постоянной основе и считать его полноценным.

## О проекте

Этот проект был создан по причине слишком неудобного получения расписания с оригинального сайта в ручную. Для облегчения жизни и был создан этот бот.

***

## Запуск

### Установка зависимостей

Для того чтобы установить все зависимости, используйте команду

```console
pip install -r requirements.txt
```

### Добавление токена

Для того чтобы добавить токен вашего бота, измените переменную TOKEN в Tokens.env, должно получится что-то типа такого

```
TOKEN = "XXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### Запуск бота

Для запуска бота достаточно просто запустить в консоли main.py

```console
python main.py
```

***

## Добавление расписания другой группы [WIP]

Для того чтобы добавить расписание другой группы, необходимо изменить файл plain_rasp.json, добавив расписание своей группы в формате json к списку groups и заменить переменную GROUP в Tokens.env

***

## Ответственность и гарантии

**Вся информация предоставляемая проектом предоставляется в исходном виде, без гарантий полноты или своевременности**, и без иных явно выраженных или подразумеваемых гарантий. Использование данного проекта происходит исключительно **по вашему усмотрению и на ваш риск**.

***

## TODO

- [ ] Адекватная поддержка нескольких групп

- [ ] Поддержка нескольких корпусов

- [ ] Оптимизация

- [ ] Кэширование данных [WIP]

***

## Запуск в докере [WIP]

***

[WIP]

[Writed by SahsaGHT(lysk) 🐲 under the supervision of Aestas as Satsea]::
