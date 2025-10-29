class SerieAlias:
    def __init__(self, db_connection):
        self.database_connection = db_connection
        self.database_cursor = self.database_connection.database_cursor

        self.database_cursor.execute("""
            CREATE TABLE IF NOT EXISTS series_alias (
                alias_name TEXT PRIMARY KEY,
                series_name TEXT NOT NULL,
                FOREIGN KEY (series_name) REFERENCES series (series_name)
            );
        """)

    def add_series_alias(self, alias_name, series_name):
        self.database_cursor.execute("INSERT OR IGNORE INTO series_alias (alias_name, series_name) VALUES (?, ?)", (alias_name, series_name))
        self.database_connection.commit()