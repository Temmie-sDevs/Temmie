import discord, re
from DAL.database import Database
from utils import read_online_spreadsheet, update_collection, send_message
from Utils.channels import add_channel, remove_channel, ChannelResult
from Utils.lf import add_lf, remove_lf, tag_add_lf, tag_remove_lf, list_lf, LFResult
from Utils.tagalert import tagalert
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

LF_COMMANDS = {
    "add": ["Add a serie to the list of series searched"],
    "remove": ["Remove a serie from the list of series searched"],
    "tag": ["Manage the list of series searched via tags", TAG_LF_COMMANDS],
    "list": ["Lists all series in your search"],
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
        case "add":
            serie = " ".join(commands[2:]).strip()
            match (add_lf(db, message, serie)):
                case LFResult.SUCCESS:
                    messageToSend = f"Serie '{serie}' added to your search."
                case LFResult.ALREADY_DID:
                    messageToSend = f"Serie '{serie}' is already in your search."
        case "remove":
            serie = " ".join(commands[2:]).strip()
            match (remove_lf(db, message, serie)):
                case LFResult.SUCCESS:
                    messageToSend = f"Serie '{serie}' removed from your search."
                case LFResult.ALREADY_DID:
                    messageToSend = f"Serie '{serie}' is not in your search."
        case "list":
            messageToSend = list_lf(db, message)
        case "tag":
            if len(commands) < 3:
                await handle_help(message, ["help", "lf", "tag"])
                return
            match commands[2].lower():
                case "add":
                    messageToSend = tag_add_lf(db, message, commands[3])
                case "remove":
                    messageToSend = tag_remove_lf(db, message, commands[3])
                case _:
                    messageToSend = "Unknown lf tag subcommand."
        case _:
            messageToSend = "Unknown lf subcommand."
    await send_message(message.channel, messageToSend)

async def handle_tagalert(db: Database, message: discord.Message, commands: list[str]):
    tag = commands[1]
    await send_message(message.channel, tagalert(db, message, tag))

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
