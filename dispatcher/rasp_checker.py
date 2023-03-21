from datetime import datetime, timedelta
from Env import hour_when_start_checking
from log import logger
from misc import sleep
from parse.requester import is_rasp_on_site
from dispatcher.messenger import start_messages_dispatching


async def start_waiting() -> None:
    while True:
        logger.info("Starting to count how much to sleep")
        weekday_number: int = datetime.today().weekday()
        time_now: datetime = datetime.now()
        time_start_hour: datetime = time_now.replace(hour=hour_when_start_checking,minute=0,second=0,microsecond=0)
        if datetime.today().hour < hour_when_start_checking and weekday_number != 6:
            time_to_sleep = time_start_hour - time_now
        else:
            match(weekday_number):
                case 5:
                    time_to_sleep = time_start_hour + timedelta(2) - time_now
                case _:
                    time_to_sleep = time_start_hour + timedelta(1) - time_now
        seconds_to_sleep: int = time_to_sleep.total_seconds()
        logger.info(f"Need to sleep for {round(seconds_to_sleep)} seconds")
        await sleep(seconds_to_sleep)
        await check_for_rasp()


async def check_for_rasp() -> None:
    attempts = 0
    while attempts < 72: # 6 hours / 300 seconds = 72
        if(is_rasp_on_site): # 10hr - 16hr = 6 hours time of possible checking 
            try:
                await start_messages_dispatching()
                break
            except:
                logger.exception(f"Something gone wrong when dispatching messages")
        attempts += 1
        await sleep(300)