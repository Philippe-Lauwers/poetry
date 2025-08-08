import faulthandler; faulthandler.enable()

from .poem_repository import PoemRepository


class PoemList:
    def __init__(self, user_id=None):
        self.poems = []
        self.fetchPoems(user_id=user_id)

    def fetchPoems(self, user_id=None):
        list = PoemRepository.list(user_id=user_id)
        return list