from .table import Table

class UserTags(Table):
    def __init__(self, db_connection):
        super().__init__(db_connection, table_name="user_tags", pk_columns=("user_id", "tag"))

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tags (
                user_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                PRIMARY KEY (user_id, tag),
                FOREIGN KEY (user_id) REFERENCES user (id)
            );
        """)
        self.db.connection.commit()