from .table import Table

class User(Table):
    def __init__(self, db_connection):
        super().__init__(db_connection, table_name="user", pk_columns=("id",))

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE
            );
        """)
        self.db.connection.commit()