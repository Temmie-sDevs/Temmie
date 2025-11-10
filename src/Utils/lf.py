#coding:utf-8

from enum import Enum, auto
import discord
from DAL.database import Database
import logging
from Utils.paginator import Paginator
from Utils.confirmationDialog import ConfirmationView

logging.basicConfig(level=logging.INFO)

MAX_LFS = 500

class LFResult(Enum):
    SUCCESS = auto()
    ALREADY_DID = auto()
    MAX_LFS = auto()

async def add_lf(db: Database, message: discord.Message, serie: str, send_message = False) -> LFResult:
    user = message.author
    if db.likeds.get(filters={"user_id":user.id, "series_name":serie}):
        if send_message:
            await message.channel.send(f"Serie `{serie}` is already in your search.")
        return LFResult.ALREADY_DID
    
    if db.likeds.count(user_id=user.id) >= MAX_LFS:
        if send_message:
            await message.channel.send(f"❌ You reached the maximum number of liked series ({MAX_LFS}).")
        return LFResult.MAX_LFS
    
    # Confirmation is series exists.
    if not db.series.get(filters={"name": serie}):
        async def confirm_add(interaction):
            db.series.insert({"name": serie})
            db.likeds.insert({"user_id": user.id, "series_name": serie})
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=f"✅ Series `{serie}` added to your search!",
                    color=discord.Color.green()
                ),
                view=None
            )

        async def cancel_add(interaction):
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=f"❌ Series `{serie}` was not added.",
                    color=discord.Color.red()
                ),
                view=None
            )

        view = ConfirmationView(user=user, on_confirm=confirm_add, on_cancel=cancel_add)
        embed = discord.Embed(
            title="⚠️ Confirm Series Addition",
            description=f"The series `{serie}` does not exist in our database.\nDo you want to add it anyway?",
            color=discord.Color.orange()
        )
        if send_message:
            await message.channel.send(embed=embed, view=view)
        return None
    
    db.likeds.insert({"user_id": user.id, "series_name": serie})
    if send_message:
        await message.channel.send(f"✅ Series **{serie}** added to your search!")
    return LFResult.SUCCESS

def remove_lf(db: Database, message: discord.Message, serie: str) -> LFResult:
    user = message.author
    if db.likeds.get(filters={"user_id":user.id, "series_name":serie}):
        db.likeds.delete(user_id=user.id, series_name=serie)
        return LFResult.SUCCESS
    return LFResult.ALREADY_DID

async def get_series_tag_lf(db: Database, message: discord.Message, tag: str, add: bool) -> tuple[set, bool]:
    cards = db.cards.get(filters={"user_id":message.author.id, "tag":tag})
    series = set()
    series_added_removed = set()
    max_reached = False

    for card in cards:
        if card["series"] in series:
            continue
        series.add(card["series"])
        if add:
            add_lf_result = await add_lf(db, message, card["series"], False)
            if (add_lf_result == LFResult.SUCCESS):
                series_added_removed.add(card["series"])
            elif add_lf_result == LFResult.MAX_LFS:
                max_reached = True
                await message.channel.send(f"❌ You reached the maximum number of liked series ({MAX_LFS}).")
                break
        else:
            if (remove_lf(db, message, card["series"]) == LFResult.SUCCESS):
                series_added_removed.add(card["series"])
    return series_added_removed, max_reached

async def tag_add_lf(db: Database, message: discord.Message, tags: list[str]) -> str:
    series_added = set()
    for tag in tags:
        series, max_reached = await get_series_tag_lf(db, message, tag, True)
        series_added.update(series)
        if max_reached:
            break

    if len(series_added) == 0:
        return 'No series added.'
    if len(series_added) < 50:
        return f'{', '.join(list(series_added))} added to your search.'
    else:
        return f'{len(series_added)} series added to your search'

async def tag_remove_lf(db: Database, message: discord.Message, tags: list[str]) -> str:
    series_removed = set()
    for tag in tags:
        series_removed.update(await get_series_tag_lf(db, message, tag, False))

    if len(series_removed) == 0:
        return 'No series removed.'
    if len(series_removed) < 50:
        return f'{', '.join(list(series_removed))} removed from your search.'
    else:
        return f'{len(series_removed)} series removed from your search'

async def tags_add_lf(db: Database, message: discord.Message, tags: list[str], exclude_tags: list[str]) -> str:
    if len(tags) == 0:
        async def confirm_add(interaction):
            user_tags = set([user_tag["tag"] for user_tag in db.user_tags.get(filters={"user_id":message.author.id})])
            tags = user_tags - set(exclude_tags)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=f"✅ All tags added to your search!",
                    color=discord.Color.green()
                ),
                view=None
            )
            await tag_add_lf(db, message, tags)

        async def cancel_add(interaction):
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=f"❌ No tag added.",
                    color=discord.Color.red()
                ),
                view=None
            )

        view = ConfirmationView(user=message.author, on_confirm=confirm_add, on_cancel=cancel_add)
        embed = discord.Embed(
            title="⚠️ Confirm Tags Addition",
            description=f"All of your tags will be used to add your liked series.\nAre your sure?",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed, view=view)
        return None
    else:
        return await tag_add_lf(db, message, tags)

async def tags_remove_lf(db: Database, message: discord.Message, tags: list[str], exclude_tags: list[str]) -> str:
    if len(tags) == 0:
        user_tags = set([user_tag["tag"] for user_tag in db.user_tags.get(filters={"user_id":message.author.id})])
        tags = user_tags - set(exclude_tags)
    return await tag_remove_lf(db, message, tags)
    
async def list_lf(db: Database, message: discord.Message, username: str = ""):
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
    if not (likeds := db.likeds.get(filters={"user_id": target_user.id})):
        if target_user.id == message.author.id:
            await message.channel.send("You have no liked series.")
        else:
            await message.channel.send(f"{target_user.display_name} has no liked series.")
        return
    
    series = sorted({lf["series_name"] for lf in likeds})
    title = ""
    if target_user.id == message.author.id:
        title = f"⭐ Your Liked Series"
    else:
        title = f"⭐ Liked Series of {target_user.display_name}"
    paginator = Paginator(series, title=title, per_page=10)
    embed = paginator.get_page_content()

    await message.channel.send(embed=embed, view=paginator)

async def like_lf(db: Database, message: discord.Message, like_filter: str, add: bool):
    filter_str = like_filter.strip("%").lower()
    starts_with = like_filter.endswith("%") and not like_filter.startswith("%")
    ends_with = like_filter.startswith("%") and not like_filter.endswith("%")
    contains = like_filter.startswith("%") and like_filter.endswith("%")

    def matches(name: str):
        name = name.lower()
        if contains:
            return filter_str in name
        elif starts_with:
            return name.startswith(filter_str)
        elif ends_with:
            return name.endswith(filter_str)
        else:
            return name == filter_str

    matched = [serie["name"] for serie in db.series.get() if matches(serie["name"])]

    if not matched:
        await message.channel.send(f"No liked series match `{like_filter}`.")
        return
    
    added_or_removed = set()
    for match in matched:
        if add:
            if await add_lf(db, message, match, False) == LFResult.SUCCESS:
                added_or_removed.add(match)
        else:
            if remove_lf(db, message, match) == LFResult.SUCCESS:
                added_or_removed.add(match)

    shown = list(added_or_removed)[:20]
    remaining = len(added_or_removed) - len(shown)
    verb = "added" if add else "removed"

    message_text = ""
    if len(added_or_removed) == 0:
        message_text = "No serie added. You already have all those series!"
    else:
        message_text = f"⭐ Series {verb}:\n```{', '.join(shown)}```"
        if remaining > 0:
            message_text += f"\n*and {remaining} others...*"

    await message.channel.send(message_text)