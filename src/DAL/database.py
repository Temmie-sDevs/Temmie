from .databaseConnection import DatabaseConnection
from .channel import Channel
from .card import Card
from .liked import Liked
from .serie import Serie
from .serie_alias import SerieAlias
from .user import User

class Database:
    def __init__(self, db_path):
        self.database_connection = DatabaseConnection(db_path)
        self.cards = Card(self.database_connection)
        self.channels = Channel(self.database_connection)
        self.likeds = Liked(self.database_connection)
        self.series = Serie(self.database_connection)
        self.serieAliases = SerieAlias(self.database_connection)
        self.users = User(self.database_connection)
        self.database_connection.commit_database()

    def close_database(self):
        self.database_connection.close_database()
