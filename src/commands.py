import discord, re
from database import init_database, close_database
from utils import read_online_spreadsheet

# Constants
COMMANDS = {
    "ping": ["Send a ping pong message to check the connection of the bot"],
    "help": ["Display a help message"],
    "channel": ["Set the channel where Temmie will be allowed to send messages"],
    "sheet": ["Download and read a spreadsheet from a karuta spreadsheet message"],
}

CHANNEL_COMMANDS = {
    "add": ["Add a channel to the list of allowed channels"],
    "remove": ["Remove a channel from the list of allowed channels"],
}

PREFIX = re.compile(r"^TM?(.+)$", re.IGNORECASE)


# Async functions
async def send_message(channel, message="", embed=None):
    await channel.send(message, embed=embed)


# Handlers
async def handle_ping(message):
    await send_message(message.channel, f"<@!{message.author.id}> Pong!")

async def handle_help(message, commands):
    if len(commands) == 1:
        embed = discord.Embed(title="Commands", description="List of commands available", color=0x00ff00)
        for command in COMMANDS:
            embed.add_field(name=command, value=COMMANDS[command][0], inline=False)
    else:
        embed = discord.Embed(title="Help", description=f"Help for command `{commands[1]}`", color=0x00ff00)
        if commands[1].lower() in COMMANDS:
            embed.add_field(name=commands[1], value=COMMANDS[commands[1].lower()][0], inline=False)
        else:
            embed.add_field(name="Error", value=f"Command `{commands[1]}` not found", inline=False)
    await send_message(message.channel, embed=embed)

async def handle_sheet(message):
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
                    for line in csv:
                        print(line)
                    await send_message(message.channel, f"Spreadsheet downloaded successfully.")
                    return
                else:
                    await send_message(message.channel, "Could not find the link to the spreadsheet.")
                    return
    await send_message(message.channel, "This is not a spreadsheet message (do ksheet to generate one)")

async def handle_message(message):
    found_prefix = PREFIX.search(message.content)

    if found_prefix:
        commands = found_prefix.group(1).split(" ")
        match commands[0].lower():
            case "ping":
                await handle_ping(message)
            case "help":
                await handle_help(message, commands)
            case "sheet":
                await handle_sheet(message)
