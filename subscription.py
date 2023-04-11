from db import update_user_by_id, get_user_by_id
from misc import create_task
from log import logger

async def get_subs(user_id: int) -> list:
    user_subs = await get_user_by_id(user_id)
    if ('subscribed_groups' in user_subs): return user_subs['subscribed_groups']
    return []
   
async def get_message_type(user_id: int) -> str:
    user_message_type = await get_user_by_id(user_id)
    if ('message_type' in user_message_type): return user_message_type['message_type']
    return None
   
async def set_sub(user_id: int, group: str) -> None:
    user_data = await get_user_by_id(user_id)
    user_subs = user_data['subscribed_groups']
    if (user_subs is None):
        user_subs = [group]
    elif(group in user_subs):
        user_subs.remove(group)
    else:
        user_subs.append(group)
    await update_user_by_id({"user_id": user_id, "subscribed_groups": user_subs})
    