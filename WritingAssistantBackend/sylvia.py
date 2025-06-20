#!/usr/bin/env python

from .poembase import PoemBase


class Poem(PoemBase):

    def __init__(self, config='config/sylvia.json'):
        super().__init__(config=config)
