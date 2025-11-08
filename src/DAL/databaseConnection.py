import sqlite3


class DatabaseConnection:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def commit_database(self):
        self.connection.commit()

    def close_database(self):
        self.connection.close()