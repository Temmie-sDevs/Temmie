import discord, csv, sqlite3, re

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

async def send_message(channel, message):
    await channel.send(message)



if __name__ == "__main__":
    intents = discord.Intents(581068273470528).default() # Intents: 581068273470528
    intents.members = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is connected to the following guild:\n')

        for guild in client.guilds:
            print(f'{guild.name} (id: {guild.id})')
    
    @client.event
    async def on_message(message: discord.Message):
        if message.author == client.user:
            return
        

        match_prefix = re.compile(r"^TM?(.+)$", re.IGNORECASE)

        result = match_prefix.search(message.content)
        if result:
            await send_message(message.channel, f"<@!{message.author.id}> {result.group(1)}")

    client.run(load_token())