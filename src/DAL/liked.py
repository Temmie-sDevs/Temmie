from .table import Table

class Liked(Table):
    def __init__(self, db_connection):
        super().__init__(db_connection, table_name="liked", pk_columns=("user_id", "series_name"))

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS liked (
                user_id INTEGER NOT NULL,
                series_name TEXT NOT NULL,
                PRIMARY KEY (user_id, series_name),
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (series_name) REFERENCES series (name)
            );
        """)
        self.db.connection.commit()