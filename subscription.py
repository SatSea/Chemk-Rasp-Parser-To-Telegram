from db import update_user_by_id, get_user_by_id

async def get_subs(user_id: int) -> list:
    user_data = await get_user_by_id(user_id)
    if (user_data is None or 'subscribed_groups' not in user_data): return []
    return user_data['subscribed_groups']
   
async def get_message_type(user_id: int) -> str:
    user_data = await get_user_by_id(user_id)
    if (user_data is None or 'message_type' not in user_data): return "Классический"
    return user_data['message_type']

async def set_sub(user_id: int, group: str) -> None:
    user_subs = await get_subs(user_id)
    if (user_subs is None):
        user_subs = [group]
    elif(group in user_subs):
        user_subs.remove(group)
    else:
        user_subs.append(group)
    await update_user_by_id({"user_id": user_id, "subscribed_groups": user_subs})
    
async def set_message_type(user_id: int, message_type: str) -> None:
    user_message_type = await get_message_type(user_id)
    if (user_message_type is None):
        user_message_type = message_type
    elif(message_type == user_message_type):
        user_message_type = message_type
    else:
        user_message_type = message_type
    await update_user_by_id({"user_id": user_id, "message_type": user_message_type})