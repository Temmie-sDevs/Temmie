import sqlite3


class DatabaseConnection:
    def __init__(self, db_path):
        self.database_connection = sqlite3.connect(db_path)
        self.database_cursor = self.database_connection.cursor()

    def commit_database(self):
        self.database_connection.commit()

    def close_database(self):
        self.database_connection.close()