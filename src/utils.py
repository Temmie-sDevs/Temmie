#coding:utf-8

import os, csv, aiohttp
from DAL.database import Database
import logging
import discord

logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "..", "database", "temmie.db")


# Async functions
async def send_message(channel: discord.TextChannel, message: str = "", embed: discord.Embed = None):
    MAX_LENGTH = 2000
    if embed is not None:
        await channel.send(message[:MAX_LENGTH], embed=embed)
        return

    while len(message) > 0:
        chunk = message[:MAX_LENGTH]
        await channel.send(chunk)
        message = message[MAX_LENGTH:]

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
    tags = set()
    db.cards.delete(user_id = user_id)
    columns = ["code", "user_id", "number", "edition", "character", "series", "tag", "wishlists"]
    for card in csv:
        filtered_data = {k: card[k] for k in columns if k in card}
        filtered_data["user_id"] = user_id
        filtered_data["number"] = int(filtered_data["number"])
        filtered_data["edition"] = int(filtered_data["edition"])
        filtered_data["wishlists"] = int(filtered_data["wishlists"])
        if db.cards.get(filters={"code": filtered_data["code"]}):
            db.cards.delete(code = filtered_data["code"])
        db.cards.insert(filtered_data)
        if filtered_data["tag"] != "":
            tags.add(filtered_data["tag"])
        series = filtered_data["series"]
        if not db.series.get(filters={"name":series}):
            db.series.insert({"name": series})
    db.user_tags.delete(user_id = user_id)
    for tag in tags:
        db.user_tags.insert({"user_id": user_id, "tag": tag})