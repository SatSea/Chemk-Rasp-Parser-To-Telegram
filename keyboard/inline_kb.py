from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from subscription import get_subs
from log import logger

async def get_inline_sub_kb(user_id: int):
    groups = ["Ит1-22", "Са1-21", "Са3-21", "С1-21", "С3-21", "Ир1-21", "Ир3-21", "Ир5-21", "С1-20", "С3-20", "Ип1-20", "Ип3-20", "Ир1-20", "Ир3-20", "Ир5-20",
              "Кс1-20", "Кс3-20", "Кс5-20", "Ип1-19", "Ип3-19", "Ир1-19", "Ир3-19", "Ир5-19", "Кс1-19", "Кс3-19", "Кс5-19", "С1-19", "С3-19", "С1-18", "С3-18"]
    subs = await get_subs(str(user_id))
    inline_keyboard_buttons = []
    for group in groups:
        inline_keyboard_buttons.append(InlineKeyboardButton(text = f"{'✅ ' if group in subs else '❌ '}{group}",callback_data=f"subscribe_{group}"))
    keyboard = InlineKeyboardBuilder()
    keyboard.add(*inline_keyboard_buttons)
    keyboard.adjust(3)
    return keyboard.as_markup(resize_keyboard=True)