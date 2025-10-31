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