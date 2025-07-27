from poem_repository import PoemRepository
from poem_repository import KeywordRepository

import faulthandler; faulthandler.enable()
import os
import pickle
import random
import re
import time
import warnings
from datetime import datetime
from functools import wraps

import numpy as np
import scipy.stats

from .poem_container import Poem as PoemContainer, Keyword, \
    KeywordSuggestion  # container to store the output in a hierarchy of Poem>>Stanza>>Verse objects
from .poem_repository import PoemRepository
from .poembase_config import PoembaseConfig
from .poemutils import count_syllables
from .verse_generator import VerseGenerator

class PoemList:
    def __init__(self, user_id=None):
        self.poems = []
        self.fetchPoems(user_id=user_id)

    def fetchPoems(self, user_id=None):
        list = PoemRepository.list(user_id=user_id)
        return list