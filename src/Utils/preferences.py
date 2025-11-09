#coding:utf-8

from enum import Enum, auto
import discord
from DAL.database import Database
import logging

logging.basicConfig(level=logging.INFO)

class PreferencesResult(Enum):
    SUCCESS = auto()
    ALREADY_DID = auto()
    INVALID = auto()

class BoolValue(Enum):
    TRUE = True
    FALSE = False
    NULL = None

def getBoolValue(value: str) -> BoolValue:
    if (value.lower() == "true" or value == "1" or value.lower() == "y" or value.lower() == "yes"):
        return BoolValue.TRUE
    elif (value.lower() == "false" or value == "0" or value.lower() == "n" or value.lower() == "no"):
        return BoolValue.FALSE
    return BoolValue.NULL

def preferences_mention(db: Database, message: discord.Message, value: str) -> PreferencesResult:
    currentValueLines = db.users.get(filters={"id":message.author.id})
    if (len(currentValueLines) != 1):
        return PreferencesResult.INVALID
    currentValue = currentValueLines[0]["mention"]
    desiredValue = getBoolValue(value)
    if (desiredValue == BoolValue.NULL):
        return PreferencesResult.INVALID
    if (desiredValue.value == currentValue):
        return PreferencesResult.ALREADY_DID
    db.users.update({"mention": desiredValue.value}, id=message.author.id)
    return PreferencesResult.SUCCESS