from db import db_instance
from log import logger

async def get_user_by_id(user_id:int) -> dict | None:
    user_data = db_instance.find_one({"user_id": user_id})
    if (user_data == None):
        logger.info("User {user_id} not found")
        return None
    return user_data

async def update_user_by_id(user_data: dict) -> None:
    try:
        user_id = {"user_id": user_data.pop("user_id")}
        update_fields = {"$set": user_data}
        db_instance.update_one(user_id, update_fields, upsert=True)
    except:
        logger.exception(f"Failed to set user data {user_data}")