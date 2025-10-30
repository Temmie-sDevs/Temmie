#coding:utf-8

from enum import Enum, auto
import discord
from DAL.database import Database
import logging

logging.basicConfig(level=logging.INFO)

class ChannelResult(Enum):
    SUCCESS = auto()
    ALREADY_DID = auto()
    ADMIN_RIGHTS = auto()

def add_channel(db: Database, message: discord.Message) -> ChannelResult:
    user = message.author
    logging.info(f"Channel ID: {message.channel.id}")
    if user.guild_permissions.administrator == True:
        return ChannelResult.ADMIN_RIGHTS

    channel_id = message.channel.id
    if not db.channels.get(id=channel_id):
        db.channels.insert({"id":channel_id})
        return ChannelResult.SUCCESS
    return ChannelResult.ALREADY_DID

def remove_channel(db: Database, message: discord.Message) -> ChannelResult:
    user = message.author
    if user.guild_permissions.administrator == True:
        return ChannelResult.ADMIN_RIGHTS

    channel_id = message.channel.id
    if db.channels.get(id=channel_id):
        db.channels.delete(id = channel_id)
        return ChannelResult.SUCCESS
    return ChannelResult.ALREADY_DID