#coding:utf-8

import discord
from DAL.database import Database
import logging

logging.basicConfig(level=logging.INFO)

class LFDto:
    def __init__(self):
        self.cards: list[str] = []
        self.users: set[int] = set()
        self.series: set[str] = set()
    def __repr__(self):
        return f"LFDto(users={list(self.users)}, series={list(self.series)}, cards={self.cards})"

def prepare_text_message(db: Database, merged: list[LFDto], author_id: str) -> str:
    lines = []

    for dto in merged:
        if not dto.users or not dto.cards or author_id in dto.users:
            continue

        users_str_list = []
        for user_id in dto.users:
            user_data = db.users.get(id=user_id)
            if not user_data:
                continue
            mention_flag = user_data[0]["mention"]
            if mention_flag:
                users_str_list.append(f"<@{user_id}>")
            else:
                users_str_list.append(f"{user_data[0]["username"]}")

        if not users_str_list:
            continue
        
        users_str = ", ".join(users_str_list)
        verb = "is" if len(dto.users) == 1 else "are"
        lines.append(f"**{users_str} {verb} looking for:**")

        cards_str = ", ".join(dto.cards)
        lines.append(f"```\n{cards_str}\n```*from series: {", ".join(dto.series)}*\n")

    return "\n".join(lines) if lines else "No one is looking for your cards."

def tagalert(db: Database, message: discord.Message, tag: str) -> str:
    guild_member_ids = {member.id for member in message.guild.members}
    cards = db.cards.get(user_id=message.author.id, tag=tag)
    likeds_in_server = [lf for lf in db.likeds.get() if lf["user_id"] in guild_member_ids]

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
    return prepare_text_message(db, merged, message.author.id)