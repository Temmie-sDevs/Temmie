#coding:utf-8

import discord, asyncio
from commands import handle_message
from DAL.database import Database
from utils import load_token, DATABASE_PATH

def main():
    CONNECTION = None # Mandatory to avoid "Error: cannot access local variable 'CONNECTION' where it is not associated with a value"
    try:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        client = discord.Client(intents=intents)

        CONNECTION: Database = Database(DATABASE_PATH)

        @client.event
        async def on_message(message: discord.Message):
            if message.author == client.user:
                return
            await handle_message(CONNECTION, message)

        @client.event
        async def on_ready():
            print(f"✅ {client.user} connected to:")
            for guild in client.guilds:
                print(f" - {guild.name} (id: {guild.id})")

        token = load_token()
        if token:
            client.run(token)
        else:
            raise FileNotFoundError("Token file not found")
    finally:
        if CONNECTION:
            CONNECTION.close_database()
        print("Database connection closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        print("Exiting...")