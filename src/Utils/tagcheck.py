#coding:utf-8

import discord
from DAL.database import Database
import logging
from utils import send_chunked_list
from Utils.paginator import Paginator

MAX_CARDS_TAG = 50

logging.basicConfig(level=logging.INFO)

async def add_tagseries(db: Database, message: discord.Message, tag: str, series: str) -> str:
    user_id = message.author.id
    series = series.lower()
    if series:
        if not db.series.get(filters={"name": series}):
            await message.channel.send(f":x: Series `{series}` has not been found.")
            return
        if db.tag_series.get(filters={"user_id": user_id, "tag": tag, "series": series}):
            await message.channel.send(f":x: Series `{series}` is already bound to the tag: `{tag}`.")    
            return    
        db.tag_series.insert({"user_id": user_id, "tag": tag, "series": series})
        await message.channel.send(f":white_check_mark: Series `{series}` has been bound to the tag: `{tag}`.")
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
        await message.channel.send(f":grey_exclamation: No series bounded to the tag: `{tag}`")
        return
    
    first_series = list(series_added)[:10]
    series_text = "\n".join(first_series)
    and_others = ""
    if len(series_added) > 10:
        and_others += f"**and {len(series_added) - 10} others**"
    await message.channel.send(f":white_check_mark: Series:\n```{series_text}```\n{and_others} bounded to tag:`{tag}`")

async def remove_tagseries(db: Database, message: discord.Message, tag: str, series: str) -> str:
    user_id = message.author.id
    series = series.lower()
    if series:
        if not db.series.get(filters={"name": series}):
            await message.channel.send(f":x: Series `{series}` has not been found.")
            return
        if not db.tag_series.get(filters={"user_id": user_id, "tag": tag, "series": series}):
            await message.channel.send(f":x: Series `{series}` is not bound to the tag: `{tag}`.")
            return
        db.tag_series.delete(user_id = user_id, tag = tag, series = series)
        await message.channel.send(f":white_check_mark: Series `{series}` bound to the tag: `{tag}` has been removed.")
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
        await message.channel.send(f":grey_exclamation: No series bound removed from the tag: `{tag}`")
        return
    
    first_series = list(series_removed)[:10]
    series_text = "\n".join(first_series)
    and_others = ""
    if len(series_removed) > 10:
        and_others += f"**and {len(series_removed) - 10} others**"
    await message.channel.send(f":white_check_mark: Series:\n```{series_text}```\n{and_others} bound removed from tag: `{tag}`")

async def tagcheck(db: Database, message: discord.Message, tag: str, exclude_tags: set):
    user_id = message.author.id
    message_sent = False

    ts_rows = db.tag_series.get(filters={"user_id": user_id}, select=["series", "tag"])
    series_to_tags: dict[str, set[str]] = {}
    registered_tags = set()
    for r in ts_rows:
        s = r["series"]
        t = r["tag"]
        if t in exclude_tags:
            continue
        series_to_tags.setdefault(s, set()).add(t)
        registered_tags.add(r["tag"])
        
    if tag:
        registered_tags = [tag]

    exclude_list = list(exclude_tags)
    placeholders = ",".join(["?"] * len(exclude_list)) if exclude_list else None
    cardsToMove: dict[str, set[str]] = {}
    for tag in registered_tags:
        query = f"""
            SELECT c.code, c.series
            FROM card c
            LEFT JOIN tag_series ts
                ON c.user_id = ts.user_id
                AND c.series = ts.series
                AND ts.tag = c.tag
            WHERE c.user_id = ?
                AND c.tag = ?
                {"AND c.tag NOT IN (" + placeholders + ")" if placeholders else ""}
                AND ts.series IS NULL;
        """
        params = [user_id, tag] + exclude_list
        db.connection.cursor.execute(query, tuple(params))
        cards = db.connection.cursor.fetchall()

        for card in cards:
            code = card["code"]
            series_name = card["series"]
            target_tags = series_to_tags.get(series_name)
            if target_tags and len(target_tags) > 0:
                cardsToMove.setdefault(list(target_tags)[0], set()).add(code)
            else:
                cardsToMove.setdefault("ut", set()).add(code)

        # To be more optimized, we do a real sql query here. The get method abstraction would require too much refactor and would become too complicated to handle this
        query2 = f"""
            SELECT c.code
            FROM card c
            JOIN tag_series ts
                ON c.user_id = ts.user_id
                AND c.series = ts.series
            WHERE c.user_id = ?
            AND ts.tag = ?
            AND c.tag != ts.tag
            {"AND c.tag NOT IN (" + placeholders + ")" if placeholders else ""};
        """
        db.connection.cursor.execute(query2, tuple(params))
        cards = db.connection.cursor.fetchall()
        for card in cards:
            cardsToMove.setdefault(tag, set()).add(card["code"])

    if cardsToMove:
        for key in sorted(cardsToMove.keys(), key=lambda k: (k == "ut", k.lower())):
            value = cardsToMove[key]
            message_sent = True
            await send_chunked_list(message.channel, f"**Tag `{key}`**", list(value), "", f"kt {key} ", MAX_CARDS_TAG)

    if not message_sent:
        await message.channel.send("Your cards are already well organized!")

    
async def list_tag_series(db: Database, message: discord.Message, username: str = ""):
    guild = message.guild
    target_user = None
    
    if message.mentions:
        target_user = message.mentions[0]
    elif username:
        username = username.strip().lower()

        # Try exact match (case-insensitive)
        for member in guild.members:
            if member.name.lower() == username or member.display_name.lower() == username:
                target_user = member
                break

        # If not found, try "starts with"
        if not target_user:
            for member in guild.members:
                if member.name.lower().startswith(username) or member.display_name.lower().startswith(username):
                    target_user = member
                    break
        # If still not found, notify
        if not target_user:
            await message.channel.send(f"❌ No user found in this server matching '{username}'.")
            return
    else:
        target_user = message.author

    # Search the user based on the whole username should match with the user name, then if not found, try to find a user starting with username.
    if not (tagseries := db.tag_series.get(filters={"user_id": target_user.id})):
        if target_user.id == message.author.id:
            await message.channel.send("You have no tag/series association.")
        else:
            await message.channel.send(f"{target_user.display_name} has no tag/series association.")
        return
    
    tagseries = sorted({f"{ts["tag"]} -> {ts["series"]}" for ts in tagseries})
    title = ""
    if target_user.id == message.author.id:
        title = f"⭐ Your Tag/Series associations"
    else:
        title = f"⭐ Tag/Series associations of {target_user.display_name}"
    paginator = Paginator(tagseries, title=title, per_page=10)
    embed = paginator.get_page_content()

    await message.channel.send(embed=embed, view=paginator)