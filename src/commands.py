import discord, re
from database import Database
from utils import read_online_spreadsheet, update_collection, add_channel, remove_channel

# Constants
CHANNEL_COMMANDS = {
    "add": ["Add a channel to the list of allowed channels"],
    "remove": ["Remove a channel from the list of allowed channels"],
}

COMMANDS_HELP = {
    "<ommands>": ["Give the help message for the specified command"],
}

COMMANDS = {
    "ping": ["Send a ping pong message to check the connection of the bot"],
    "help": ["Display a help message", COMMANDS_HELP],
    "channel": ["Set the channel where Temmie will be allowed to send messages", CHANNEL_COMMANDS],
    "sheet": ["Download and read a spreadsheet from a karuta spreadsheet message"],
}


PREFIX = re.compile(r"^TM?(.+)$", re.IGNORECASE)


# Async functions
async def send_message(channel: discord.TextChannel, message: str = "", embed: discord.Embed = None):
    await channel.send(message, embed=embed)


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
        if replied_msg.author.id == 646937666251915264 and replied_msg.embeds:
            if replied_msg.embeds[0].title == "Collection Spreadsheet":
                description = replied_msg.embeds[0].description
                spreadsheet_owner = description.split(",")[0].strip()
                print(f"Spreadsheet owner: {spreadsheet_owner}")
                if "https://" in description:
                    link = description.split("(")[1].split(")")[0]
                    csv = await read_online_spreadsheet(link)
                    update_collection(db, message.author.id, csv)

                    await send_message(message.channel, f"Spreadsheet downloaded successfully.")
                    return
                else:
                    await send_message(message.channel, "Could not find the link to the spreadsheet.")
                    return
    await send_message(message.channel, "This is not a spreadsheet message (do ksheet to generate one)")

async def handle_channel(db: Database, message: discord.Message, commands: list[str]):
    match commands[1].lower():
        case "add":
            match (add_channel(db, message)):
                case 0:
                    await send_message(message.channel, f"Channel <#{message.channel.id}> added to allowed channels.")
                case 1:
                    await send_message(message.channel, f"Channel <#{message.channel.id}> is already an allowed channel.")
                case 2:
                    await send_message(message.channel, "You need to be an administrator to use this command.")
        case "remove":
            match (remove_channel(db, message)):
                case 0:
                    await send_message(message.channel, f"Channel <#{message.channel.id}> removed from allowed channels.")
                case 1:
                    await send_message(message.channel, f"Channel <#{message.channel.id}> is not an allowed channel.")
                case 2:
                    await send_message(message.channel, "You need to be an administrator to use this command.")
        case _:
            await send_message(message.channel, "Unknown channel subcommand.")

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
