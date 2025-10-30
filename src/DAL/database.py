from .databaseConnection import DatabaseConnection
from .channel import Channel
from .card import Card
from .liked import Liked
from .series import Series
from .series_alias import SeriesAlias
from .user import User

class Database:
    def __init__(self, db_path):
        self.connection = DatabaseConnection(db_path)
        self.cards = Card(self.connection)
        self.channels = Channel(self.connection)
        self.likeds = Liked(self.connection)
        self.series = Series(self.connection)
        self.serieAliases = SeriesAlias(self.connection)
        self.users = User(self.connection)
        self.connection.commit_database()

    def close_database(self):
        self.connection.close_database()
