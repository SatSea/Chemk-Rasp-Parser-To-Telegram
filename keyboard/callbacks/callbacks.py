from init_bot import dp
from subscription import set_sub
from keyboard.inline_kb import get_inline_sub_kb
from aiogram.types import CallbackQuery
from aiogram import F, Dispatcher
from log import logger


async def subscription(callback: CallbackQuery):
    try:
        await set_sub(callback.from_user.id, (callback.data).replace("subscribe_", ""))
        await callback.answer()
        await callback.message.edit_reply_markup(reply_markup=await get_inline_sub_kb(callback.from_user.id))
        logger.info(
            f"Got callback \"subscription\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
    except:
        logger.exception(
            f"Failed to process callback \"subscription\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
        await callback.answer(text="Не удалось подписатся/отписатся от расписания группы", show_alert=True)


async def unknown_callback(callback: CallbackQuery):
    await callback.answer(text=f"Неизвестный callback: {callback.data}", show_alert=True)


async def register_callbacks(dp: Dispatcher):
    dp.callback_query.register(subscription, F.data.startswith("subscribe_"))
    dp.callback_query.register(unknown_callback)
