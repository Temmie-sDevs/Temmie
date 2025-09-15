#coding:utf-8

import os, csv, aiohttp


DATABASE_PATH = "../database/temmie.db"
CONNECTION = None


def compute_csv(csv_text) -> list[dict]:
    spamreader = csv.reader(csv_text.splitlines(), dialect='excel')
    header = next(spamreader)
    cards = []
    for row in spamreader:
        cards.append({header[i]: row[i] for i in range(len(row))})
    return cards

def sort_cards(cards, key):
    cards.sort(key=lambda x: int(x[key]))
    return cards

def load_token():
    if os.path.exists("../.token"):
        with open("../.token", "r") as f:
            return f.read().split("\n")[0]
    else:
        print("Token file not found")
        return None
    
async def read_online_spreadsheet(url) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return compute_csv(await resp.text())
            else:
                raise Exception(f"Failed to download file: {resp.status}")