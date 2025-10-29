class Liked:
    def __init__(self, db_connection):
        self.database_connection = db_connection
        self.database_cursor = self.database_connection.database_cursor

        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS liked (
                user_id INTEGER NOT NULL,
                series_name TEXT NOT NULL,
                PRIMARY KEY (user_id, series_name),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (series_name) REFERENCES series (series_name)
            );
        """)