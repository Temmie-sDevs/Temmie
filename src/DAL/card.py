from .table import Table

class Card(Table):
    def __init__(self, db_connection):
        super().__init__(db_connection, table_name="card", pk_columns=("code",))

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS card (
                code TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                number INTEGER NOT NULL,
                edition INTEGER NOT NULL,
                character TEXT NOT NULL,
                series TEXT NOT NULL,
                tag TEXT NOT NULL,
                wishlists INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (series) REFERENCES series (name)
            );
        """)
        self.db.connection.commit()