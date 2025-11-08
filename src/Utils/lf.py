#coding:utf-8

from enum import Enum, auto
import discord
from DAL.database import Database
import logging

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

def tag_add_lf(db: Database, message: discord.Message, tag: str) -> str:
    cards = db.cards.get(user_id=message.author.id, tag=tag)
    series = set()
    series_added = set()

    for card in cards:
        if card["series"] not in series:
            series.add(card["series"])
            if (add_lf(db, message, card["series"]) == LFResult.SUCCESS):
                series_added.add(card["series"])

    if len(series_added) == 0:
        return 'No series added.'
    return f'{', '.join(list(series_added))} added to your search.'

def tag_remove_lf(db: Database, message: discord.Message, tag: str) -> str:
    cards = db.cards.get(user_id=message.author.id, tag=tag)
    series = set()
    series_removed = set()

    for card in cards:
        if card["series"] not in series:
            series.add(card["series"])
            if (remove_lf(db, message, card["series"]) == LFResult.SUCCESS):
                series_removed.add(card["series"])

    if len(series_removed) == 0:
        return 'No series removed.'
    return f'{', '.join(list(series_removed))} removed from your search.'

def list_lf(db: Database, message: discord.Message) -> str:
    if not (likeds := db.likeds.get(user_id=message.author.id)):
        return "You have no liked series."
    series = sorted({lf["series_name"] for lf in likeds})
    return f'**Here are the series you\'re looking for:\n**```{', '.join(series)}```'