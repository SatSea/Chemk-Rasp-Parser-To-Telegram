import logging
from os import getenv
from dotenv import load_dotenv

if (load_dotenv("Env/Tokens.env") == False):
    logging.error("Failed to load env")
    raise Exception("Failed to load env")
try:
    token = getenv('TOKEN')
    groups = getenv('GROUP')
    name_of_group = getenv('NAME_OF_GROUP')
    allowed_ids = list(map(int, getenv('ALLOWED_IDS').split(',')))
    hour_when_start_checking = int(getenv('START_HOUR'))
    logging.info("Variables from env loaded successfully")
except:
    logging.error("Failed to load data from env")
    raise Exception("Failed to load data from env")