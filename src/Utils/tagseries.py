#coding:utf-8

import discord
from DAL.database import Database
import logging
from enum import Enum, auto

logging.basicConfig(level=logging.INFO)

class TagSeriesResult(Enum):
    SUCCESS = auto()
    ALREADY_DID = auto()
    NOT_FOUND = auto()

async def add_tagseries(db: Database, message: discord.Message, tag: str, series: str) -> str:
    user_id = message.author.id
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
        and_others += f"and {len(series_added) - 10} others"
    await message.channel.send(f"Series:\n```{series_text}```\n**{and_others}** bounded to tag:`{tag}`")

async def remove_tagseries(db: Database, message: discord.Message, tag: str, series: str) -> str:
    user_id = message.author.id
    if series:
        if not db.series.get(filters={"name": series}):
            await message.channel.send(f"Series `{series}` has not been found.")
            return
        if not db.tag_series.get(filters={"user_id": user_id, "tag": tag, "series": series}):
            await message.channel.send(f"Series `{series}` is not bound to the tag: `{tag}`.")
            return
        db.tag_series.delete(user_id = user_id, tag = tag, series = series_name)
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
        and_others += f"and {len(series_removed) - 10} others"
    await message.channel.send(f"Series:\n```{series_text}```\n**{and_others}** bound removed from tag: `{tag}`")
