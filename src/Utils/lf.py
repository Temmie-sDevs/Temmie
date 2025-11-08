#coding:utf-8

from enum import Enum, auto
import discord
from DAL.database import Database
import logging
from Utils.paginator import Paginator

logging.basicConfig(level=logging.INFO)

class LFResult(Enum):
    SUCCESS = auto()
    ALREADY_DID = auto()

def add_lf(db: Database, message: discord.Message, serie: str) -> LFResult:
    user = message.author
    if not db.likeds.get(user_id=user.id, series_name=serie):
        if not db.series.get(name=serie):
            db.series.insert({"name": serie})
        db.likeds.insert({"user_id": user.id, "series_name": serie})
        return LFResult.SUCCESS
    return LFResult.ALREADY_DID

def remove_lf(db: Database, message: discord.Message, serie: str) -> LFResult:
    user = message.author
    if db.likeds.get(user_id=user.id, series_name=serie):
        db.likeds.delete(user_id=user.id, series_name=serie)
        return LFResult.SUCCESS
    return LFResult.ALREADY_DID

def get_series_tag_lf(db: Database, message: discord.Message, tag: str, add: bool) -> set:
    cards = db.cards.get(user_id=message.author.id, tag=tag)
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

def tags_add_lf(db: Database, message: discord.Message, tags: list[str]) -> str:
    series_added = set()
    for tag in tags:
        series_added.update(get_series_tag_lf(db, message, tag, True))

    if len(series_added) == 0:
        return 'No series added.'
    return f'{', '.join(list(series_added))} added to your search.'

def tags_remove_lf(db: Database, message: discord.Message, tags: list[str]) -> str:
    series_removed = set()
    for tag in tags:
        series_removed.update(get_series_tag_lf(db, message, tag, False))

    if len(series_removed) == 0:
        return 'No series removed.'
    return f'{', '.join(list(series_removed))} removed from your search.'

async def list_lf(db: Database, message: discord.Message):
    if not (likeds := db.likeds.get(user_id=message.author.id)):
        return "You have no liked series."
    series = sorted({lf["series_name"] for lf in likeds})

    paginator = Paginator(series, title="⭐ Your Liked Series", per_page=10)
    embed = paginator.get_page_content()

    await message.channel.send(embed=embed, view=paginator)