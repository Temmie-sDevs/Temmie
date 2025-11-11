#coding:utf-8

import discord
from DAL.database import Database
import logging
from utils import send_chunked_list

MAX_CARDS_TAG = 50

logging.basicConfig(level=logging.INFO)

async def add_tagseries(db: Database, message: discord.Message, tag: str, series: str) -> str:
    user_id = message.author.id
    series = series.lower()
    if series:
        if not db.series.get(filters={"name": series}):
            await message.channel.send(f"Series `{series}` has not been found.")
            return
        if db.tag_series.get(filters={"user_id": user_id, "tag": tag, "series": series}):
            await message.channel.send(f"Series `{series}` is already bound to the tag: `{tag}`.")    
            return    
        db.tag_series.insert({"user_id": user_id, "tag": tag, "series": series})
        await message.channel.send(f"Series `{series}` has been bound to the tag: `{tag}`.")
        return

    series = db.cards.get(filters={"user_id": user_id, "tag": tag}, select=["series"], distinct=True)
    series_added = set()
    for serie in series:
        series_name = serie["series"]
        if not db.series.get(filters={"name": series_name}):
            db.series.insert({"name": series_name})
        if db.tag_series.get(filters={"user_id": user_id, "tag": tag, "series": series_name}):
            continue
        db.tag_series.insert({"user_id": user_id, "tag": tag, "series": series_name})
        series_added.add(series_name)

    if len(series_added) == 0:
        await message.channel.send(f"No series bounded to the tag: `{tag}`")
        return
    
    first_series = list(series_added)[:10]
    series_text = "\n".join(first_series)
    and_others = ""
    if len(series_added) > 10:
        and_others += f"**and {len(series_added) - 10} others**"
    await message.channel.send(f"Series:\n```{series_text}```\n{and_others} bounded to tag:`{tag}`")

async def remove_tagseries(db: Database, message: discord.Message, tag: str, series: str) -> str:
    user_id = message.author.id
    series = series.lower()
    if series:
        if not db.series.get(filters={"name": series}):
            await message.channel.send(f"Series `{series}` has not been found.")
            return
        if not db.tag_series.get(filters={"user_id": user_id, "tag": tag, "series": series}):
            await message.channel.send(f"Series `{series}` is not bound to the tag: `{tag}`.")
            return
        db.tag_series.delete(user_id = user_id, tag = tag, series = series)
        await message.channel.send(f"Series `{series}` bound to the tag: `{tag}` has been removed.")
        return
        
    series = db.cards.get(filters={"user_id": user_id, "tag": tag}, select=["series"], distinct=True)
    series_removed = set()
    for serie in series:
        series_name = serie["series"]
        if not db.series.get(filters={"name": series_name}):
            db.series.insert({"name": series_name})
        if not db.tag_series.get(filters={"user_id": user_id, "tag": tag, "series": series_name}):
            continue
        db.tag_series.delete(user_id = user_id, tag = tag, series = series_name)
        series_removed.add(series_name)
        
    if len(series_removed) == 0:
        await message.channel.send(f"No series bound removed from the tag: `{tag}`")
        return
    
    first_series = list(series_removed)[:10]
    series_text = "\n".join(first_series)
    and_others = ""
    if len(series_removed) > 10:
        and_others += f"**and {len(series_removed) - 10} others**"
    await message.channel.send(f"Series:\n```{series_text}```\n{and_others} bound removed from tag: `{tag}`")

async def tagcheck(db: Database, message: discord.Message, tag: str):
    user_id = message.author.id
    message_sent = False

    ts_rows = db.tag_series.get(filters={"user_id": user_id}, select=["series", "tag"])
    series_to_tags: dict[str, set[str]] = {}
    registered_tags = set()
    for r in ts_rows:
        s = r["series"]
        t = r["tag"]
        series_to_tags.setdefault(s, set()).add(t)
        registered_tags.add(r["tag"])
        
    if tag:
        registered_tags = [tag]

    cardsToMove: dict[str, set[str]] = {}
    for tag in registered_tags:
        query = """
            SELECT c.code, c.series
            FROM card c
            LEFT JOIN tag_series ts
                ON c.user_id = ts.user_id
                AND c.series = ts.series
                AND ts.tag = c.tag
            WHERE c.user_id = ?
                AND c.tag = ?
                AND ts.series IS NULL;
        """
        params = (user_id, tag)
        db.connection.cursor.execute(query, params)
        cards = db.connection.cursor.fetchall()

        for card in cards:
            code = card["code"]
            series_name = card["series"]
            target_tags = series_to_tags.get(series_name)
            if target_tags and len(target_tags) > 0:
                cardsToMove.setdefault(list(target_tags)[0], set()).add(code)
            else:
                cardsToMove.setdefault("ut", set()).add(code)

        # To be more optimized, we do a real sql query here. The get method abstraction would require too much refactor and would become too complicated to handle this
        query2 = """
            SELECT c.code
            FROM card c
            JOIN tag_series ts
                ON c.user_id = ts.user_id
                AND c.series = ts.series
            WHERE c.user_id = ?
            AND ts.tag = ?
            AND c.tag != ts.tag;
        """
        db.connection.cursor.execute(query2, params)
        cards = db.connection.cursor.fetchall()
        for card in cards:
            cardsToMove.setdefault(tag, set()).add(card["code"])

    if cardsToMove:
        for key in sorted(cardsToMove.keys(), key=lambda k: (k == "ut", k.lower())):
            value = cardsToMove[key]
            message_sent = True
            await send_chunked_list(message.channel, f"**Tag `{key}`**", list(value), "", f"kt {key} ", MAX_CARDS_TAG)

    if not message_sent:
        await message.channel.send("Your cards are already well organized!")


# TODO List tagseries
# TODO except for tagcheck, like i want to check tags but do not care about except
# Set emojis to boud remove, ... to know easily