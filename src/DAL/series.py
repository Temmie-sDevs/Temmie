from .table import Table

class Series(Table):
    def __init__(self, db_connection):
        super().__init__(db_connection, table_name="series", pk_columns=("name",))

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS series (
                name TEXT PRIMARY KEY
            );
        """)
        self.db.connection.commit()