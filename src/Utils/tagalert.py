#coding:utf-8

import discord
from DAL.database import Database
import logging

MAX_TA_CARDS=10000

logging.basicConfig(level=logging.INFO)

class LFDto:
    def __init__(self):
        self.cards: list[str] = []
        self.users: set[int] = set()
        self.series: set[str] = set()
    def __repr__(self):
        return f"LFDto(users={list(self.users)}, series={list(self.series)}, cards={self.cards})"

async def prepare_text_message(channel: discord.TextChannel, merged: list[LFDto], author_id: str, users_info: dict[int, dict[str, any]]) -> str:
    MAX_LENGTH = 2000
    MAX_DISPLAY = 10

    for dto in merged:
        if not dto.users or not dto.cards or author_id in dto.users:
            continue

        users_list = [
            f"<@{uid}>" if users_info[uid]["mention"] else users_info[uid]["username"]
            for uid in dto.users if uid in users_info
        ]
        if not users_list:
            continue

        if len(users_list) > MAX_DISPLAY:
            displayed_users = users_list[:MAX_DISPLAY]
            remaining_count = len(users_list) - MAX_DISPLAY
            users_str = ", ".join(displayed_users) + f", and {remaining_count} other{'s' if remaining_count > 1 else ''}"
        else:
            users_str = ", ".join(users_list)

        verb = "is" if len(users_list) == 1 else "are"
        header = f"**{users_str} {verb} looking for:**\n"
        
        series_list = list(dto.series)
        if len(series_list) > MAX_DISPLAY:
            displayed_series = series_list[:MAX_DISPLAY]
            remaining_count = len(series_list) - MAX_DISPLAY
            series_str = ", ".join(displayed_series) + f", and {remaining_count} other{'s' if remaining_count > 1 else ''}"
        else:
            series_str = ", ".join(series_list)

        footer_series = f"**__from series__**: *{series_str}*\n"

        # Split cards into chunks per message
        chunks = []
        current_chunk = []
        current_len = len(header) + len(footer_series) + 8

        for card in dto.cards:
            card_len = len(card) + 2  # comma + space
            if current_len + card_len > MAX_LENGTH:
                chunks.append(", ".join(current_chunk))
                current_chunk = []
                current_len = len(header) + len(footer_series) + 8
            current_chunk.append(card)
            current_len += card_len

        if current_chunk:
            chunks.append(", ".join(current_chunk))

        # Send messages
        first_chunk = chunks.pop(0)
        await channel.send(f"{header}```\n{first_chunk}\n```{footer_series}")

        for chunk in chunks:
            await channel.send(f"```\n{chunk}\n```")

async def tagalert(db: Database, message: discord.Message, tag: str) -> str:
    guild_member_ids = {member.id for member in message.guild.members}
    cards = db.cards.get(filters={"user_id": message.author.id, "tag": tag})[:MAX_TA_CARDS]

    if not cards:
        await message.channel.send("No cards found for this tag.")
        return
    
    likeds_in_server = db.likeds.get(in_filters={"user_id": list(guild_member_ids)})
    user_ids = {lf["user_id"] for lf in likeds_in_server}
    users_info = {u["id"]: u for u in db.users.get(in_filters={"id": list(user_ids)})}

    series_map: dict[str, LFDto] = {}
    for card in cards:
        key = card["series"].lower()
        dto = series_map.setdefault(key, LFDto())
        dto.cards.append(card["code"])
        dto.series.add(key)
    
    for lf in likeds_in_server:
        key = lf["series_name"].lower()
        if key in series_map:
            dto = series_map[key]
            dto.users.add(lf["user_id"])

    merged_map: dict[tuple[int, ...], LFDto] = {}
    for dto in series_map.values():
        key = tuple(sorted(dto.users)) if dto.users else tuple()
        if key in merged_map:
            merged_map[key].cards.extend(dto.cards)
            merged_map[key].series.update(dto.series)
        else:
            merged_map[key] = dto
    merged = list(merged_map.values())
    await prepare_text_message(message.channel, merged, message.author.id, users_info)