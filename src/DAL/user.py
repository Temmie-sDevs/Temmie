class User:
    def __init__(self, db_connection):
        self.database_connection = db_connection
        self.database_cursor = self.database_connection.database_cursor

        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE
            );
        """)

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