from init_bot import dp
from subscription import set_sub, get_subs
from aiogram.types import CallbackQuery
from aiogram import F
from log import logger

@dp.callback_query_handler(F.text.startswith("subscribe_"))
async def subscription(callback: CallbackQuery):
    try:
        await set_sub(callback.from_user.id,(callback.data).replace("subscribe_",""))
        logger.info(f"Got callback \"subscription\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
        callback.message.edit_reply_markup(await get_subs(callback.from_user.id))
    except:
        logger.exception(f"Failed to process callback \"subscription\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")