from aiogram import types
from db import get_user_by_id
from keyboard.inline_kb import get_inline_groups_kb

async def default_group(user_id: int) -> tuple[bool, str | None]:
    user_data = await get_user_by_id(user_id)
    if (user_data is None or 'default_group' not in user_data): return False, None
    return True, user_data['default_group']

async def rasp_without_default_group(message: types.Message, day: str) -> None:
    await message.reply("Ты не выбрал свою группу по умолчанию, так что выбирай кнопочками:\n(или поставь свою группу через [WIP])",reply_markup=await get_inline_groups_kb(day))

