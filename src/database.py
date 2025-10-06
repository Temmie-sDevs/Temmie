import sqlite3

def init_database(db_path):
    database_connection = sqlite3.connect(db_path)
    database_cursor = database_connection.cursor()

    # Create channels table
    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            channel_id INTEGER PRIMARY KEY
        );
    """)

    # Create series table
    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS series (
            series_name TEXT PRIMARY KEY
        );
    """)

    # Create series alias table
    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS series_alias (
            alias_name TEXT PRIMARY KEY,
            series_name TEXT NOT NULL,
            FOREIGN KEY (series_name) REFERENCES series (series_name)
        );
    """)

    # Create users table
    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE
        );
    """)

    # Create liked table
    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS liked (
            user_id INTEGER NOT NULL,
            series_name TEXT NOT NULL,
            PRIMARY KEY (user_id, series_name),
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (series_name) REFERENCES series (series_name)
        );
    """)

    # Create cards table
    database_cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            card_code INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            card_number INTEGER NOT NULL,
            card_edition INTEGER NOT NULL,
            card_character TEXT NOT NULL,
            card_series TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (card_series) REFERENCES series (series_name)
        );
    """)

    database_connection.commit()
    return database_connection, database_cursor

def close_database(connection):
    connection.close()

def add_channel(cursor, channel_id):
    cursor.execute("INSERT INTO channels (channel_id) VALUES (?)", (channel_id,))
    cursor.connection.commit()

def remove_channel(cursor, channel_id):
    cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
    cursor.connection.commit()

def get_channels(cursor, channel_id=None):
    if channel_id:
        cursor.execute("SELECT channel_id FROM channels WHERE channel_id = ?", (channel_id,))
    else:
        cursor.execute("SELECT channel_id FROM channels")
    return cursor.fetchall()

def add_user(cursor, user_id, username):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    cursor.connection.commit()

def remove_user(cursor, user_id):
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    cursor.connection.commit()

def get_users_by_name(cursor, username):
    cursor.execute("SELECT user_id, username FROM users WHERE username LIKE ?", ('%' + username + '%',))
    return cursor.fetchall()

def get_user_by_id(cursor, user_id):
    cursor.execute("SELECT user_id, username FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def add_series(cursor, series_name):
    cursor.execute("INSERT OR IGNORE INTO series (series_name) VALUES (?)", (series_name,))
    cursor.connection.commit()

def remove_series(cursor, series_name):
    cursor.execute("DELETE FROM series WHERE series_name = ?", (series_name,))
    cursor.connection.commit()

def get_series(cursor):
    cursor.execute("SELECT series_name FROM series")
    return cursor.fetchall()

def add_series_alias(cursor, alias_name, series_name):
    cursor.execute("INSERT OR IGNORE INTO series_alias (alias_name, series_name) VALUES (?, ?)", (alias_name, series_name))
    cursor.connection.commit()