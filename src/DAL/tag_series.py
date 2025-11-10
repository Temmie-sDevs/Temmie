from .table import Table

class TagSeries(Table):
    def __init__(self, db_connection):
        super().__init__(db_connection, table_name="tag_series", pk_columns=("user_id", "tag", "series"))

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_series (
                user_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                series TEXT NOT NULL,
                PRIMARY KEY (user_id, tag, series),
                FOREIGN KEY (user_id) REFERENCES user (id)
                FOREIGN KEY (series) REFERENCES series (name)
            );
        """)
        self.db.connection.commit()