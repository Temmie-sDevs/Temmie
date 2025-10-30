from .table import Table

class Channel(Table):
    def __init__(self, db_connection):
        super().__init__(db_connection, table_name="channel", pk_columns=("id",))

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel (
                id INTEGER PRIMARY KEY
            );
        """)
        self.db.connection.commit()