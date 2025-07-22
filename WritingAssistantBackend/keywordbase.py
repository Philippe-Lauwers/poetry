#!/usr/bin/env python

import sys
import random
import time
import numpy as np
import pickle
import os
import re
import numpy as np
import scipy.stats
import kenlm
from datetime import datetime
import codecs
import warnings
from functools import reduce
import copy

from .poemutils import count_syllables, hmean
import re
from pprint import pprint
import onmt
import argparse
import torch
import json
import warnings

from .verse_generator import VerseGenerator
from .poem_container import Poem as PoemContainer, Stanza, Verse, Keyword, KeywordSuggestion # container to store the output in a hierarchy of Poem>>Stanza>>Verse objects
from .poembase_config import PoembaseConfig
from .poem_repository import PoemRepository, StanzaRepository, VerseRepository, KeywordRepository
import time
from functools import wraps


warnings.filterwarnings("ignore")

class KeywordBase:

    def __init__(self, lang, form, nmfDim=0, title=None, poemId=None):

        self.lang = lang # store the language for this instance of the PoemBase class

        self.initializeConfig(lang)
        self.loadNMFData()
        self.generator = VerseGenerator(self.MODEL_FILE, self.entropy_threshold)
        self.loadVocabulary()
        self._poemContainer = PoemContainer(lang=lang, form=form, nmfDim=nmfDim, id=poemId)
        if title is not None:
            self._poemContainer.title = title
            self._title = title

        if not os.path.exists('log'):
            os.makedirs('log')
        logfile = 'log/poem_' + datetime.now().strftime("%Y%m%d")
        self.log = open(logfile, 'a')

    @property
    def container(self):
        return self._poemContainer
    @container.setter
    def container(self, myContainer):
        self._poemContainer = myContainer

    def timed(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            print(f"[{func.__name__}] start @ {t0 * 1000:.3f} ms")
            result = func(*args, **kwargs)
            t1 = time.perf_counter()
            elapsed_ms = (t1 - t0) * 1000
            print(f"[{func.__name__}] end   @ {t1 * 1000:.3f} ms")
            print(f"[{func.__name__}] elapsed: {elapsed_ms:.3f} ms")
            return result

        return wrapper

    def initializeConfig(self, lang):

        """with open(config) as json_config_file:
            configData = json.load(json_config_file)"""
        
        location = os.path.join(
            PoembaseConfig.getParameter(category='general', parameterName='data_directory', language=lang),
            PoembaseConfig.getParameter(category='general', parameterName='language', language=lang)
        )
            
        self.NMF_FILE = os.path.join(location, PoembaseConfig.getParameter(category='nmf', parameterName='matrix_file', language=lang))
        self.NMF_DESCRIPTION_FILE = os.path.join(location, PoembaseConfig.getParameter(category='nmf', parameterName='description_file', language=lang))
        self.MODEL_FILE = os.path.join(location, PoembaseConfig.getParameter(category='model', parameterName='parameter_file', language=lang))

        self.name = PoembaseConfig.getParameter(category='general', parameterName='name', language=lang)
        self.entropy_threshold = float(
            PoembaseConfig.getParameter(category='poem', parameterName='entropy_threshold', language=lang))
        self.suggestionBatchSize = int(
            PoembaseConfig.getParameter(category='poem', parameterName='suggestion_batch_size', language=lang))

    def loadNMFData(self):
        self.W = np.load(self.NMF_FILE)
        with open(self.NMF_DESCRIPTION_FILE, 'rb') as f:
            self.nmf_descriptions = pickle.load(f, encoding='utf8')
        
    def loadVocabulary(self):
        self.i2w = self.generator.vocab.itos
        self.w2i = self.generator.vocab.stoi

    # def receiveUserInput(self, title=None, form=None, nmfDim=None, userInput=None, structure=None):
    #     self.initPoemContainer(form=form, nmfDim=nmfDim, lang=self.lang, origin='browser', title=title)
    #     # Stores a representation of the poem in the database
    #     self.container.receiveUserInput(userInput, structure, title)
    #     PoemRepository.save(self.container)

    # @timed
    def fetch(self, n = 0, inputKeywords = {}):
        keywordCollections = []
        nmfDims = []
        nmfDim = (0,0)

        self.container.receiveUserInput(inputKeywords, [], self._title)

        titleWords = []
        if self._title != "":
            titleWords.append(re.sub(r"(?:[^\w\s]|_)+", '', self._title).split(" "))

        if inputKeywords:
            hasKeywordText = False
            for kw in inputKeywords.values():
                if kw != "":
                    hasKeywordText = True
                    break

        if not inputKeywords or not hasKeywordText:
            for sugg in range(self.suggestionBatchSize):
                for i in range(16):
                    keywordCollection = []
                    for i in range(n):
                        keywordCollection.append(self.get1Keyword())
                    for j in range(len(self.nmf_descriptions)):
                        if titleWords:
                            nmfScore = self.checkNMF(list(set(keywordCollection)|set(titleWords)), [j])
                        else:
                            nmfScore = self.checkNMF(keywordCollection, [j])
                        if nmfScore > nmfDim[1]:
                            scorelist = list(nmfDim)
                            scorelist[0] = j
                            scorelist[1] = nmfScore
                            nmfDim = tuple(scorelist)
                keywordCollections.append(keywordCollection)
                nmfDims.append(nmfDim[0])
            for sugg in range(n):
                if sugg > len(self.container.keywords) - 1 or ():
                    kw = Keyword("")
                    self.container.keywords.append(kw)
                else:
                    kw = self.container.keywords[sugg]


                for i in range(len(keywordCollections)):
                    kws = KeywordSuggestion(keywordCollections[i][sugg])
                    kws.nmfDim = nmfDims[i]
                    kw.suggestions.append(kws)
            PoemRepository.save(self.container)
        else:
            keywordCollections[0] = inputKeywords

        return self.container.to_dict()

    def get1Keyword(self):
        cntSyl = 0
        n = 0
        while cntSyl < 3 or (n > 16 and cntSyl < 2):
            kw = random.choice(self.i2w)
            n += 1
            cntSyl = count_syllables(kw)[1]
            pass
        pass
        return kw



    def checkSyllablesScore(self, words, mean, std):
        gaussian = scipy.stats.norm(mean,std)
        nSyllables = sum([count_syllables(w)[1] for w in words])
        return gaussian.pdf(nSyllables) / 0.19

    def computeNMFScore(self,words,dimList):
        sm = 0
        sm = sum([max(self.W[self.w2i[w],dimList]) for w in words if w in self.w2i])
        return sm

    def checkNMF(self, words, dimList):
        # words = list(set([w for w in words if not w in self.blacklist_words]))
        NMFTop = np.max(np.max(self.W[:,dimList], axis=0))
        NMFScore = self.computeNMFScore(words, dimList)
        return NMFScore / NMFTop

