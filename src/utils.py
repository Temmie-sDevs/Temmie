#coding:utf-8

import os, csv, aiohttp
from DAL.database import Database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "..", "database", "temmie.db")


def compute_csv(csv_text: str) -> list[dict]:
    spamreader = csv.reader(csv_text.splitlines(), dialect='excel')
    header = next(spamreader)
    cards = []
    for row in spamreader:
        cards.append({header[i]: row[i] for i in range(len(row))})
    return cards

def sort_cards(cards: list[dict], key: str) -> list[dict]:
    cards.sort(key=lambda x: int(x[key]))
    return cards

def load_token() -> str | None:
    if os.path.exists(os.path.join(BASE_DIR, "..", ".token")):
        with open(os.path.join(BASE_DIR, "..", ".token"), "r") as f:
            return f.read().split("\n")[0]
    else:
        print("Token file not found")
        return None

async def read_online_spreadsheet(url: str) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return compute_csv(await resp.text())
            else:
                raise Exception(f"Failed to download file: {resp.status}")

def update_collection(db: Database, user_id: int, csv: list[dict]):
    pass