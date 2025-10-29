class Channel:
    def __init__(self, db_connection):
        self.database_connection = db_connection
        self.database_cursor = self.database_connection.database_cursor

        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY
            );
        """)

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