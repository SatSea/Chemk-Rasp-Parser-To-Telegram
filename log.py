import logging

logging_level = logging.INFO
logging_mode = "a"

logging.basicConfig(level=logging_level, encoding='utf-8',
                    format="%(asctime)s %(levelname)s %(message)s")

logger = logging.getLogger()
logger.setLevel(logging_level)

handler = logging.FileHandler(f"logs/logging.log", mode=logging_mode)
handler2 = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s %(asctime)s %(message)s")

handler.setFormatter(formatter)
handler2.setFormatter(formatter)

logger.handlers = [handler,handler2]

