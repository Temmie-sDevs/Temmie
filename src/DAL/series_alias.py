from .table import Table

class SeriesAlias(Table):
    def __init__(self, db_connection):
        super().__init__(db_connection, table_name="series_alias", pk_columns=("name",))

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS series_alias (
                name TEXT PRIMARY KEY,
                series_name TEXT NOT NULL,
                FOREIGN KEY (series_name) REFERENCES series (name)
            );
        """)
        self.db.connection.commit()