#coding:utf-8

import discord
from DAL.database import Database
import logging
from utils import send_message, send_chunked_list

logging.basicConfig(level=logging.INFO)

async def burnalert(db: Database, message: discord.Message, tag: str, wl_throttle: int = 10, print_throttle: int = 1000) -> str:
    cards = db.cards.get(filters={"user_id": message.author.id, "tag": tag})

    if not cards:
        await message.channel.send("No cards found for this tag.")
        return
    
    wishlists = set()
    midprints = set()
    lowprints = set()
    singleprints = set()
    firstprints = set()

    wishlists_sum = 0
    midprints_sum = 0
    lowprints_sum = 0
    singleprints_sum = 0
    firstprints_sum = 0
    
    for card in cards:
        if card["wishlists"] >= wl_throttle:
            wishlists.add(card["code"])
            wishlists_sum += card["wishlists"]
        if card["number"] >= print_throttle:
            continue
        if card["number"] >= 100:
            midprints.add(card["code"])
            midprints_sum += card["number"]
        elif card["number"] >= 10:
            lowprints.add(card["code"])
            lowprints_sum += card["number"]
        elif card["number"] > 1:
            singleprints.add(card["code"])
            singleprints_sum += card["number"]
        elif card["number"] == 1:
            firstprints.add(card["code"])
            firstprints_sum += card["number"]

    wishlists_list = list(wishlists)
    midprints_list = list(midprints)
    lowprints_list = list(lowprints)
    singleprints_list = list(singleprints)
    firstprints_list = list(firstprints)

    message_sent = False
    if len(wishlists_list) > 0:
        message_sent = True
        avg = round(wishlists_sum / len(wishlists_list), 2)
        footer = f"*Total wishlists value: {wishlists_sum}*\n*Average wishlists value: {avg}*"
        await send_chunked_list(message.channel, "High wishlisted cards", wishlists_list, footer)

    if len(midprints_list) > 0:
        message_sent = True
        avg = round(midprints_sum / len(midprints_list), 2)
        await send_chunked_list(message.channel, "Mid print cards", midprints_list, f"*Average print: {avg}*")

    if len(lowprints_list) > 0:
        message_sent = True
        avg = round(lowprints_sum / len(lowprints_list), 2)
        await send_chunked_list(message.channel, "Low print cards", lowprints_list, f"*Average print: {avg}*")

    if len(singleprints_list) > 0:
        message_sent = True
        avg = round(singleprints_sum / len(singleprints_list), 2)
        await send_chunked_list(message.channel, "Single print cards", singleprints_list, f"*Average print: {avg}*")

    if len(firstprints_list) > 0:
        message_sent = True
        avg = round(firstprints_sum / len(firstprints_list), 2)
        await send_chunked_list(message.channel, "First print cards", firstprints_list, f"*Average print: {avg}*")

    if not message_sent:
        await send_message(message.channel, "No card found for this tag for these parameters")