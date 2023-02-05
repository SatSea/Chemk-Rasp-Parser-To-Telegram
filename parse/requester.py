import aiohttp
from bs4 import BeautifulSoup
from pandas import read_html
from cachetools import cached, TTLCache


# def get_from_site(day):
#     responce = requests.get(f"https://rsp.chemk.org/4korp/{day}.htm")
#     responce.encoding = 'windows-1251'
#     contents = responce.text
#     soup = BeautifulSoup(contents, "html.parser")
#     schedule_on_site = not (soup.find("div", class_="Section1"))
#     if schedule_on_site:
#         return contents
#     return None

@cached(cache=TTLCache(maxsize=1024, ttl=60)) # limit site requests to 60 seconds
async def req_site(day: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://rsp.chemk.org/4korp/{day}.htm") as response:
            text = await response.text()
            
async def check_rasp_on_site(day: str) -> bool:
    '''
    if true, there is a rasp on the site
    if false, there is no rasp on the site
    '''
    raw_rasp = await req_site(day)
    soup = BeautifulSoup(raw_rasp, "html.parser")
    return not (soup.find("div", class_="Section1"))

async def get_table_rasp(day: str) -> list[str]:
    raw_rasp = await req_site(day)
    return read_html(raw_rasp, thousands=None)[0].values.tolist()

