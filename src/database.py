import sqlite3


class Database:
    def __init__(self, db_path):
        self.database_connection = sqlite3.connect(db_path)
        self.database_cursor = self.database_connection.cursor()

        # Create channels table
        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY
            );
        """)

        # Create series table
        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS series (
                series_name TEXT PRIMARY KEY
            );
        """)

        # Create series alias table
        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS series_alias (
                alias_name TEXT PRIMARY KEY,
                series_name TEXT NOT NULL,
                FOREIGN KEY (series_name) REFERENCES series (series_name)
            );
        """)

        # Create users table
        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE
            );
        """)

        # Create liked table
        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS liked (
                user_id INTEGER NOT NULL,
                series_name TEXT NOT NULL,
                PRIMARY KEY (user_id, series_name),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (series_name) REFERENCES series (series_name)
            );
        """)

        # Create cards table
        self.database_cursor.execute("""
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

        self.database_connection.commit()

    def close_database(self):
        self.database_connection.close()

    def add_channel(self, channel_id):
        self.database_cursor.execute("INSERT INTO channels (channel_id) VALUES (?)", (channel_id,))
        self.database_connection.commit()

    def remove_channel(self, channel_id):
        self.database_cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        self.database_connection.commit()

    def get_channels(self, channel_id=None):
        if channel_id:
            self.database_cursor.execute("SELECT channel_id FROM channels WHERE channel_id = ?", (channel_id,))
        else:
            self.database_cursor.execute("SELECT channel_id FROM channels")
        return self.database_cursor.fetchall()

    def add_user(self, user_id, username):
        self.database_cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        self.database_connection.commit()

    def remove_user(self, user_id):
        self.database_cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.database_connection.commit()

    def get_users_by_name(self, username):
        self.database_cursor.execute("SELECT user_id, username FROM users WHERE username LIKE ?", ('%' + username + '%',))
        return self.database_cursor.fetchall()

    def get_user_by_id(self, user_id):
        self.database_cursor.execute("SELECT user_id, username FROM users WHERE user_id = ?", (user_id,))
        return self.database_cursor.fetchone()

    def add_series(self, series_name):
        self.database_cursor.execute("INSERT OR IGNORE INTO series (series_name) VALUES (?)", (series_name,))
        self.database_connection.commit()

    def remove_series(self, series_name):
        self.database_cursor.execute("DELETE FROM series WHERE series_name = ?", (series_name,))
        self.database_connection.commit()

    def get_series(self):
        self.database_cursor.execute("SELECT series_name FROM series")
        return self.database_cursor.fetchall()

    def add_series_alias(self, alias_name, series_name):
        self.database_cursor.execute("INSERT OR IGNORE INTO series_alias (alias_name, series_name) VALUES (?, ?)", (alias_name, series_name))
        self.database_connection.commit()