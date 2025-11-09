import discord, re
from DAL.database import Database
from utils import read_online_spreadsheet, update_collection, send_message
from Utils.channels import add_channel, remove_channel, ChannelResult
from Utils.lf import add_lf, remove_lf, tag_add_lf, tag_remove_lf, tags_add_lf, tags_remove_lf, list_lf, LFResult, MAX_LFS
from Utils.tagalert import tagalert
from Utils.preferences import preferences_mention, PreferencesResult
from Utils.burnalert import burnalert
from Config.const import KARUTA_ID

# Constants
CHANNEL_COMMANDS = {
    "add": ["Add a channel to the list of allowed channels"],
    "remove": ["Remove a channel from the list of allowed channels"],
}

TAG_LF_COMMANDS = {
    "add": ["Add all series contained in a tag to your search"],
    "remove": ["Remove all series contained in a tag from your search"],
}

TAGS_LF_COMMANDS = {
    "add": ["Add all series contained in all tags to your search, except tags after tmlf tags add e:{t1},{t2}, ..."],
    "remove": ["Remove all series contained in all tags to your search, except tags after tmlf tags remove e:{t1},{t2}, ..."],
}

LF_COMMANDS = {
    "add": ["Add a serie to the list of series searched"],
    "remove": ["Remove a serie from the list of series searched"],
    "tag": ["Manage the list of series searched via tags", TAG_LF_COMMANDS],
    "tags": ["Manage the list of series searched via all tags", TAGS_LF_COMMANDS],
    "list": ["Lists all series in your search"],
}

PREFERENCES_COMMANDS = {
    "mention": ["Authorize the bot to mention yourself or not. Usage: tmpreferences mention (true|false)"],
}

COMMANDS_HELP = {
    "<commands>": ["Give the help message for the specified command"],
}

COMMANDS = {
    "ping": ["Send a ping pong message to check the connection of the bot"],
    "help": ["Display a help message", COMMANDS_HELP],
    "channel": ["Set the channel where Temmie will be allowed to send messages", CHANNEL_COMMANDS],
    "sheet": ["Download and read a spreadsheet from a karuta spreadsheet message"],
    "lf": ["Manage the list of series searched", LF_COMMANDS],
    "tagalert": ["Alert users looking for a card which is in your tag {tag}"],
    "preferences": ["Manage your preferences", PREFERENCES_COMMANDS],
    "burnalert": ["Displays cards that shouldn't be burnt from your tag {tag}"],
}


PREFIX = re.compile(r"^TM?(.+)$", re.IGNORECASE)


# Handlers
async def handle_ping(message: discord.Message):
    await send_message(message.channel, f"<@!{message.author.id}> Pong!")

async def handle_help(message: discord.Message, commands: list[str]):
    if len(commands) == 1:
        embed = discord.Embed(title="Commands", description="List of commands available", color=0x00ff00)
        for command in COMMANDS:
            if len(COMMANDS[command]) > 1 and isinstance(COMMANDS[command][1], dict):
                subcommands = "\n".join([f" - `{sub}`: {COMMANDS[command][1][sub][0]}" for sub in COMMANDS[command][1]])
                embed.add_field(name=command, value=f"{COMMANDS[command][0]}\nSubcommands:\n{subcommands}", inline=False)
            else:
                embed.add_field(name=command, value=COMMANDS[command][0], inline=False)
    else:
        embed = discord.Embed(title="Help", description=f"Help for command `{commands[1]}`", color=0x00ff00)
        if commands[1].lower() in COMMANDS:
            if len(COMMANDS[commands[1].lower()]) > 1 and isinstance(COMMANDS[commands[1].lower()][1], dict):
                subcommands = "\n".join([f" - `{sub}`: {COMMANDS[commands[1].lower()][1][sub][0]}" for sub in COMMANDS[commands[1].lower()][1]])
                embed.add_field(name=commands[1], value=f"{COMMANDS[commands[1].lower()][0]}\nSubcommands:\n{subcommands}", inline=False)
            else:
                embed.add_field(name=commands[1], value=COMMANDS[commands[1].lower()][0], inline=False)
        else:
            embed.add_field(name="Error", value=f"Command `{commands[1]}` not found", inline=False)
    await send_message(message.channel, embed=embed)

async def handle_sheet(db: Database, message: discord.Message):
    if (message.type == discord.MessageType.reply):
        replied_msg = await message.channel.fetch_message(message.reference.message_id)
        if replied_msg.author.id == KARUTA_ID and replied_msg.embeds:
            if replied_msg.embeds[0].title == "Collection Spreadsheet":
                description = replied_msg.embeds[0].description
                spreadsheet_owner = description.split(",")[0].strip()
                print(f"Spreadsheet owner: {spreadsheet_owner}")
                if "https://" in description:
                    link = description.split("(")[1].split(")")[0]
                    csv = await read_online_spreadsheet(link)
                    loading_msg  = await send_loading_message(message.channel)
                    update_collection(db, message.author.id, csv)
                    await update_to_success(loading_msg, len(csv))
                    if not db.users.get(filters={"id": message.author.id}):
                        db.users.insert({"id": message.author.id, "username": message.author.name})
                    return
                else:
                    await send_message(message.channel, "Could not find the link to the spreadsheet.")
                    return
    await send_message(message.channel, "This is not a spreadsheet message (do ksheet to generate one)")

async def send_loading_message(channel: discord.TextChannel):
    embed = discord.Embed(
        title="⏳ Loading all your cards...",
        description="Please wait while I fetch your Karuta collection.",
        color=discord.Color.yellow()
    )

    loading_message = await channel.send(embed=embed)
    return loading_message


async def update_to_success(loading_message: discord.Message, count: int):
    embed = discord.Embed(
        title="✅ Cards Loaded!",
        description=f"Successfully imported **{count}** cards into your collection.",
        color=discord.Color.green()
    )

    await loading_message.edit(embed=embed)

async def handle_channel(db: Database, message: discord.Message, commands: list[str]):
    messageToSend = ""
    match commands[1].lower():
        case "add":
            match (add_channel(db, message)):
                case ChannelResult.SUCCESS:
                    messageToSend = f"Channel <#{message.channel.id}> added to allowed channels."
                case ChannelResult.ALREADY_DID:
                    messageToSend = f"Channel <#{message.channel.id}> is already an allowed channel."
                case ChannelResult.ADMIN_RIGHTS:
                    messageToSend = "You need to be an administrator to use this command."
        case "remove":
            match (remove_channel(db, message)):
                case ChannelResult.SUCCESS:
                    messageToSend = f"Channel <#{message.channel.id}> removed from allowed channels."
                case ChannelResult.ALREADY_DID:
                    messageToSend = f"Channel <#{message.channel.id}> is not an allowed channel."
                case ChannelResult.ADMIN_RIGHTS:
                    messageToSend = "You need to be an administrator to use this command."
        case _:
            messageToSend = "Unknown channel subcommand."
    await send_message(message.channel, messageToSend)

async def handle_lf(db: Database, message: discord.Message, commands: list[str]):
    messageToSend = ""
    match commands[1].lower():
        case "add" | "a":
            if len(commands) < 3:
                await handle_help(message, ["help", "lf"])
                return
            serie = " ".join(commands[2:]).strip()
            match (add_lf(db, message, serie)):
                case LFResult.SUCCESS:
                    messageToSend = f"Serie '{serie}' added to your search."
                case LFResult.ALREADY_DID:
                    messageToSend = f"Serie '{serie}' is already in your search."
                case LFResult.MAX_LFS:
                    messageToSend = f"You reached the maximum of {MAX_LFS} liked series."
        case "remove" | "rm" | "r":
            if len(commands) < 3:
                await handle_help(message, ["help", "lf"])
                return
            serie = " ".join(commands[2:]).strip()
            match (remove_lf(db, message, serie)):
                case LFResult.SUCCESS:
                    messageToSend = f"Serie '{serie}' removed from your search."
                case LFResult.ALREADY_DID:
                    messageToSend = f"Serie '{serie}' is not in your search."
        case "list" | "l":
            if len(commands) > 2:
                await list_lf(db, message, commands[2])
            else:
                await list_lf(db, message)
        case "tag" | "t":
            if len(commands) < 4:
                await handle_help(message, ["help", "lf", "tag"])
                return
            tags_input = " ".join(commands[3:])
            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            match commands[2].lower():
                case "add" | "a":
                    messageToSend = tag_add_lf(db, message, tags)
                case "remove" | "rm" | "r":
                    messageToSend = tag_remove_lf(db, message, tags)
                case _:
                    messageToSend = "Unknown lf tag subcommand."
        case "tags":
            if len(commands) < 3:
                await handle_help(message, ["help", "lf", "tags"])
                return
            
            raw_args = " ".join(commands[3:]).strip()
            # Default: no exclusions, all tags
            tags = set()
            exclude_tags = set()

            if raw_args:
                # Split by space, then handle "except:" or "e:"
                for part in raw_args.split():
                    part = part.strip()
                    if part.lower().startswith(("except:", "e:", "e=")):
                        sep_index = part.find(":") if ":" in part else part.find("=")
                        values_str = part[sep_index+1:].strip()
                        exclude_tags.update({v.strip() for v in values_str.split(",") if v.strip()})
                    else:
                        tags.update({v.strip() for v in part.split(",") if v.strip()})
            tags = tags - exclude_tags
            
            match commands[2].lower():
                case "add" | "a":
                    messageToSend = tags_add_lf(db, message, tags, exclude_tags)
                case "remove" | "rm" | "r":
                    messageToSend = tags_remove_lf(db, message, tags, exclude_tags)
                case _:
                    messageToSend = "Unknown lf tags subcommand."
            
        case _:
            messageToSend = "Unknown lf subcommand."
    if messageToSend:
        await send_message(message.channel, messageToSend)

async def handle_tagalert(db: Database, message: discord.Message, commands: list[str]):
    tag = commands[1]
    await tagalert(db, message, tag)

async def handle_preferences(db: Database, message: discord.Message, commands: list[str]):
    messageToSend = ""
    match commands[1].lower():
        case "mention" | "m":
            if len(commands) < 3:
                await handle_help(message, ["help", "preferences", "mention"])
                return
            value = commands[2]
            match (preferences_mention(db, message, value)):
                case PreferencesResult.SUCCESS:
                    messageToSend = f"The mention preference has successfully been set to '{value}'."
                case PreferencesResult.ALREADY_DID:
                    messageToSend = f"The mention preference is already set to '{value}'."
                case PreferencesResult.INVALID:
                    messageToSend = f"The choice is invalid '{value}' or you're not registered in the database. Please ensure you did your tmsheet."
        case _:
            messageToSend = "Unknown lf subcommand."
    if messageToSend:
        await send_message(message.channel, messageToSend)

async def handle_burnalert(db: Database, message: discord.Message, commands: list[str]):
    tag = commands[1]
    args = {"w": None, "p": None}
    arg_pattern = re.compile(r"(\w+)\s*[:=]\s*([\w.-]+)")
    for cmd in commands[2:]:
        match = arg_pattern.match(cmd)
        if match:
            key, value = match.groups()
            if key == "wl":
                key = "w"
            if key in args:
                try:
                    args[key] = float(value) if "." in value else int(value)
                except ValueError:
                    args[key] = value

    w = args["w"] or 10
    p = args["p"] or 1000

    await burnalert(db, message, tag, wl_throttle=w, print_throttle=p)

async def handle_message(db: Database, message: discord.Message):
    
    found_prefix = PREFIX.search(message.content)

    if found_prefix:
        commands = found_prefix.group(1).split(" ")
        match commands[0].lower():
            case "ping":
                await handle_ping(message)
            case "help":
                await handle_help(message, commands)
            case "sheet":
                await handle_sheet(db, message)
            case "channel":
                if len(commands) < 2:
                    await handle_help(message, ["help", "channel"])
                    return
                await handle_channel(db, message, commands)
            case "lf":
                if len(commands) < 2:
                    await handle_help(message, ["help", "lf"])
                    return
                await handle_lf(db, message, commands)
            case "tagalert" | "ta":
                if len(commands) < 2:
                    await handle_help(message, ["help", "tagalert"])
                    return
                await handle_tagalert(db, message, commands)
            case "preferences" | "p":
                if len(commands) < 3:
                    await handle_help(message, ["help", "preferences"])
                    return
                await handle_preferences(db, message, commands)
            case "burnalert" | "ba":
                if len(commands) < 2:
                    await handle_help(message, ["help", "burnalert"])
                    return
                await handle_burnalert(db, message, commands)
