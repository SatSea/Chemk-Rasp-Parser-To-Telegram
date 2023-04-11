from pymongo import MongoClient, database
from log import logger
from Env import mogno_host, mogno_port, mogno_db_name


def connect_to_db()-> MongoClient:
    try:
        return MongoClient(mogno_host, mogno_port)
    except:
        logger.exception("Failed to connect to the database")
        # logger.info("Disabling functionality related to the database")
        # return none
        # will be someday later, now we just throw an exception
        raise Exception("Failed to connect to the database")

    
    

def setup_db_instance() -> database:
    mongo_client = connect_to_db()
    try:
        db_instance = mongo_client[mogno_db_name]["users"]
        logger.info("Successfully connected to the database and got the table")
        return db_instance
    except:
        logger.exception("Failed to connect to the database")
        raise Exception("Failed to connect to the database")
    

db_instance = setup_db_instance()