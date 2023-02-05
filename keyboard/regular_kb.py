from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def get_regular_kb():
    kb = [
        [
            KeyboardButton(text="/FAQ"),
            KeyboardButton(text="/Today"),
            KeyboardButton(text="/Tomorrow")
        ],
        [
            KeyboardButton(text="/Subscribe"),
            KeyboardButton(text="/Schedule")
        ]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True)
    return keyboard