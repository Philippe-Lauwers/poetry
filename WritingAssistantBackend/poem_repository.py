from sqlalchemy import inspect
import dbModel
from poem_handle import Poem, Stanza, Verse


class PoemRepository:
    def __init__(self, poem):
        self.poem = poem
        print("poem")


class StanzaRepository:
    def __init__(self, stanza):
        self.stanza = stanza
        print("stanza")


class VerseRepository:
    def __init__(self, verse):
        self.verse = verse
        print("verse")


class KeywordRepository:
    def __init__(self, keyword):
        self.keyword = keyword
        print(keyword)
