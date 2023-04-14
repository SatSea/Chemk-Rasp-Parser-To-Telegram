from init_bot import dp, bot
from subscription import set_sub, set_message_type
from keyboard.inline_kb import get_inline_sub_kb, get_inline_message_type_kb
from aiogram.types import CallbackQuery
from aiogram import F, Dispatcher
from log import logger
from parse import group_rasp


async def subscription(callback: CallbackQuery):
    try:
        await set_sub(callback.from_user.id, callback.data.replace("subscribe_", ""))
        await callback.answer()
        await callback.message.edit_reply_markup(reply_markup=await get_inline_sub_kb(callback.from_user.id))
        logger.info(
            f"Got callback \"subscription\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
    except:
        logger.exception(
            f"Failed to process callback \"subscription\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
        await callback.answer(text="Не удалось подписаться/отписаться от расписания группы", show_alert=True)

async def message_type(callback: CallbackQuery):
    try:
        await set_message_type(callback.from_user.id, callback.data.replace("messageType_", ""))
        await callback.answer()
        await callback.message.edit_reply_markup(reply_markup=await get_inline_message_type_kb(callback.from_user.id))
        logger.info(
            f"Got callback \"message_type\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
    except:
        logger.exception(
            f"Failed to process callback \"message_type\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
        await callback.answer(text="Не удалось изменить формат сообщения", show_alert=True)

async def rasp(callback: CallbackQuery):
    try:
        rasp = await group_rasp(*callback.data.replace("rasp_", "").split("_"), callback.from_user.id)
        await bot.send_message(callback.from_user.id,rasp)
        await callback.answer()
        logger.info(
            f"Got callback \"rasp\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
    except:
        logger.exception(
            f"Failed to process callback \"rasp\" from {callback.from_user.username} ({callback.from_user.full_name}) [{callback.from_user.id}]")
        await callback.answer(text="Не удалось получить расписание :(", show_alert=True)

async def unknown_callback(callback: CallbackQuery):
    await callback.answer(text=f"Неизвестный callback: {callback.data}", show_alert=True)


async def register_callbacks(dp: Dispatcher):
    dp.callback_query.register(subscription, F.data.startswith("subscribe_"))
    dp.callback_query.register(message_type, F.data.startswith("messageType_"))
    dp.callback_query.register(rasp, F.data.startswith("rasp_"))
    dp.callback_query.register(unknown_callback)
