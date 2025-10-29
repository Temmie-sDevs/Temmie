class Card:
    def __init__(self, db_connection):
        self.database_connection = db_connection
        self.database_cursor = self.database_connection.database_cursor

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