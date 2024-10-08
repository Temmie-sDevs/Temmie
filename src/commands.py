import discord, csv, sqlite3, re


# Constants
COMMANDS = {
    "ping": ["Send a ping pong message to check the connection of the bot"],
    "help": ["Display a help message"],
    "channel": ["Set the channel where Temmie will be allowed to send messages"],
}

CHANNEL_COMMANDS = {
    "add": ["Add a channel to the list of allowed channels"],
    "remove": ["Remove a channel from the list of allowed channels"],
}

PREFIX = re.compile(r"^TM?(.+)$", re.IGNORECASE)


# Basic functions
def compute_csv(file):
    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, dialect='excel')
        header = next(spamreader)
        cards = []
        for row in spamreader:
            cards.append({header[i]: row[i] for i in range(len(row))})
    return cards

def sort_cards(cards, key):
    cards.sort(key=lambda x: int(x[key]))
    return cards

def load_token():
    with open("../.token", "r") as f:
        return f.read().split("\n")[0]


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
        embed = discord.Embed(title="Help", description=f"Help for command {commands[1]}", color=0x00ff00)
        if commands[1].lower() in COMMANDS:
            embed.add_field(name=commands[1], value=COMMANDS[commands[1].lower()][0], inline=False)
        else:
            embed.add_field(name="Error", value=f"Command {commands[1]} not found", inline=False)
    await send_message(message.channel, embed=embed)


# Main
def main():
    intents = discord.Intents(581068273470528).default() # Intents: 581068273470528
    intents.members = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message: discord.Message):
        if message.author == client.user:
            return

        result = PREFIX.search(message.content)
        if result:
            commands = result.group(1).split(" ")
            match commands[0].lower():
                case "ping":
                    await handle_ping(message)
                case "help":
                    await handle_help(message, commands)

    @client.event
    async def on_ready():
        print(f'{client.user} is connected to the following guild:\n')
        for guild in client.guilds:
            print(f'{guild.name} (id: {guild.id})')
    
    client.run(load_token())


if __name__ == "__main__":
    main()