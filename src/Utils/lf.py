#coding:utf-8

from enum import Enum, auto
import discord
from DAL.database import Database
import logging
from Utils.paginator import Paginator

logging.basicConfig(level=logging.INFO)

MAX_LFS = 500

class LFResult(Enum):
    SUCCESS = auto()
    ALREADY_DID = auto()
    MAX_LFS = auto()

def add_lf(db: Database, message: discord.Message, serie: str) -> LFResult:
    user = message.author
    if not db.likeds.get(filters={"user_id":user.id, "series_name":serie}):
        if db.likeds.count(user_id=user.id) >= MAX_LFS:
            return LFResult.MAX_LFS
        if not db.series.get(filters={"name":serie}):
            db.series.insert({"name": serie})
        db.likeds.insert({"user_id": user.id, "series_name": serie})
        return LFResult.SUCCESS
    return LFResult.ALREADY_DID

def remove_lf(db: Database, message: discord.Message, serie: str) -> LFResult:
    user = message.author
    if db.likeds.get(filters={"user_id":user.id, "series_name":serie}):
        db.likeds.delete(user_id=user.id, series_name=serie)
        return LFResult.SUCCESS
    return LFResult.ALREADY_DID

def get_series_tag_lf(db: Database, message: discord.Message, tag: str, add: bool) -> set:
    cards = db.cards.get(filters={"user_id":message.author.id, "tag":tag})
    series = set()
    series_added_removed = set()

    for card in cards:
        if card["series"] not in series:
            series.add(card["series"])
            if (add):
                if (add_lf(db, message, card["series"]) == LFResult.SUCCESS):
                    series_added_removed.add(card["series"])
            else:
                if (remove_lf(db, message, card["series"]) == LFResult.SUCCESS):
                    series_added_removed.add(card["series"])
    return series_added_removed

def tag_add_lf(db: Database, message: discord.Message, tags: list[str]) -> str:
    series_added = set()
    for tag in tags:
        series_added.update(get_series_tag_lf(db, message, tag, True))

    if len(series_added) == 0:
        return 'No series added.'
    if len(series_added) < 50:
        return f'{', '.join(list(series_added))} added to your search.'
    else:
        return f'{len(series_added)} series added to your search'

def tag_remove_lf(db: Database, message: discord.Message, tags: list[str]) -> str:
    series_removed = set()
    for tag in tags:
        series_removed.update(get_series_tag_lf(db, message, tag, False))

    if len(series_removed) == 0:
        return 'No series removed.'
    if len(series_removed) < 50:
        return f'{', '.join(list(series_removed))} removed from your search.'
    else:
        return f'{len(series_removed)} series removed from your search'

def tags_add_lf(db: Database, message: discord.Message, tags: list[str], exclude_tags: list[str]) -> str:
    if len(tags) == 0:
        user_tags = set([user_tag["tag"] for user_tag in db.user_tags.get(filters={"user_id":message.author.id})])
        tags = user_tags - set(exclude_tags)
    return tag_add_lf(db, message, tags)

def tags_remove_lf(db: Database, message: discord.Message, tags: list[str], exclude_tags: list[str]) -> str:
    if len(tags) == 0:
        user_tags = set([user_tag["tag"] for user_tag in db.user_tags.get(filters={"user_id":message.author.id})])
        tags = user_tags - set(exclude_tags)
    return tag_remove_lf(db, message, tags)
    
async def list_lf(db: Database, message: discord.Message):
    if not (likeds := db.likeds.get(filters={"user_id":message.author.id})):
        return "You have no liked series."
    series = sorted({lf["series_name"] for lf in likeds})

    paginator = Paginator(series, title="⭐ Your Liked Series", per_page=10)
    embed = paginator.get_page_content()

    await message.channel.send(embed=embed, view=paginator)