#coding:utf-8

import discord, asyncio
from commands import handle_message
from database import init_database, close_database
from utils import load_token, CONNECTION, DATABASE_PATH

def main():
    intents = discord.Intents(581068273470528).default() # Intents: 581068273470528
    intents.members = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    CONNECTION, cursor = init_database(DATABASE_PATH)

    @client.event
    async def on_message(message: discord.Message):
        if message.author == client.user:
            return
        await handle_message(message)

    @client.event
    async def on_ready():
        print(f'{client.user} is connected to the following guild:\n')
        for guild in client.guilds:
            print(f'{guild.name} (id: {guild.id})')

    token = load_token()
    if token:
        client.run(token)
    else:
        raise FileNotFoundError("Token file not found")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        if CONNECTION:
            close_database(CONNECTION)
        print(f"Error: {e}")
        print("Exiting...")