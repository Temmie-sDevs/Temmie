import sqlite3

def init_database():
    database_connection = sqlite3.connect(DATABASE_PATH)
    database_cursor = database_connection.cursor()

    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            channel_id INTEGER PRIMARY KEY
        )
    """)

    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS guild (
            guild_id INTEGER PRIMARY KEY
        );
    """)

    database_connection.commit()

    return database_connection, database_cursor

def add_channel(cursor, channel_id):
    cursor.execute("INSERT INTO channels (channel_id) VALUES (?)", (channel_id,))
    cursor.connection.commit()

def remove_channel(cursor, channel_id):
    cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
    cursor.connection.commit()

def get_channels(cursor):
    cursor.execute("SELECT channel_id FROM channels")
    return cursor.fetchall()

def add_guild(cursor, guild_id):
    cursor.execute("INSERT INTO guild (guild_id) VALUES (?)", (guild_id,))
    cursor.connection.commit()

def remove_guild(cursor, guild_id):
    cursor.execute("DELETE FROM guild WHERE guild_id = ?", (guild_id,))
    cursor.connection.commit()