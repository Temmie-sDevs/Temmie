class Serie:
    def __init__(self, db_connection):
        self.database_connection = db_connection
        self.database_cursor = self.database_connection.database_cursor

        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS series (
                series_name TEXT PRIMARY KEY
            );
        """)

    def add_series(self, series_name):
        self.database_cursor.execute("INSERT OR IGNORE INTO series (series_name) VALUES (?)", (series_name,))
        self.database_connection.commit()

    def remove_series(self, series_name):
        self.database_cursor.execute("DELETE FROM series WHERE series_name = ?", (series_name,))
        self.database_connection.commit()

    def get_series(self):
        self.database_cursor.execute("SELECT series_name FROM series")
        return self.database_cursor.fetchall()