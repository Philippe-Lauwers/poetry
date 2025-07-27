#!/usr/bin/env python
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

    def save(self, inputKeywords = {}, userInput ={}, structure = []):
        # Stores a representation of the poem in the database
        allInput = {}
        allInput.update(inputKeywords)
        allInput.update(userInput)
        self.container.receiveUserInput(allInput, structure, self._title)

        # Once the first verse is saved by the user, we don't re-evaluate the NMF dimensions
        # checkNmfDim = True
        # for k in userInput.keys():
        #     if k.startswith("v") and not k.endswith("-tmp"):
        #         checkNmfDim = False
        # <--- on second thoughts, we will always change the NMF dimension, according to the title and keywords
        # if checkNmfDim:

        if self.container.title:
            titleWords = [w.lower() for w in re.sub(r"(?:[^\w\s]|_)+", '', self.container.title).split(" ")]
        else:
            titleWords = []
        if inputKeywords:
            keywords = [w.lower() for w in inputKeywords.values()]
            self.inputKeywordsList = keywords
        else:
            keywords = []
            self.inputKeywordsList = []
        if userInput:
            # test = [re.sub(r"(?:[^\w\s]|_)+", '', vrs).lower for vrs in userInput.values() if vrs != ""]
            # test2 = ' '.join(
            #     [re.sub(r"(?:[^\w\s]|_)+", '', vrs).lower for vrs in userInput.values() if vrs != ""])
            self.inputWordsList = [word.lower()
                        for sentence in userInput.values() if sentence.strip()
                        for word in re.sub(r"[^\w\s]", "", sentence).split()
                        ] if userInput.values() else []
            pass
        else:
            self.inputWordsList = []

        nmfDim = (0,0)
        for i in range(len(self.nmf_descriptions)):
            if titleWords:
                nmfScore = self.checkNMF(list(set(titleWords) | set(keywords) | set(self.inputWordsList)), [i])
                if nmfScore > nmfDim[1]:
                    scorelist = list(nmfDim)
                    scorelist[0] = i
                    scorelist[1] = nmfScore
                    nmfDim = tuple(scorelist)
        self.container.nmfDim = nmfDim[0]
        PoemRepository.save(self.container)
        return {'status':True,'nmfDim':nmfDim[0]}

    # @timed
    def fetch(self, n = 0, inputKeywords = {}, userInput = {}, structure = []):
        allInput = {}
        allInput.update(inputKeywords)
        allInput.update(userInput)

        keywordCollections = []
        nmfDims = []
        nmfDim = (0,0)

        self.container.receiveUserInput(allInput, structure, self._title)

        if self.container.title:
            titleWords = [w.lower() for w in re.sub(r"(?:[^\w\s]|_)+", '', self.container.title).split(" ")]
        else:
            titleWords = []
        if inputKeywords:
            keywords = [w.lower() for w in inputKeywords.values()]
            self.inputKeywordsList = keywords
        else:
            keywords = []
            self.inputKeywordsList = []
        if userInput:
            self.inputWordsList = ' '.join(
                [re.sub(r"(?:[^\w\s]|_)+", '', vrs).lower() for vrs in userInput.values() if vrs != ""]).split()
        else:
            self.inputWordsList = []

        for sugg in range(self.suggestionBatchSize):
            for i in range(16):
                keywordCollection = []
                for i in range(n):
                    keywordCollection.append(self.get1Keyword())
                for j in range(len(self.nmf_descriptions)):
                    nmfScore = self.checkNMF(list(set(keywordCollection)|set(titleWords)|set(self.inputWordsList)), [j])
                    if nmfScore > nmfDim[1]:
                        scorelist = list(nmfDim)
                        scorelist[0] = j
                        scorelist[1] = nmfScore
                        nmfDim = tuple(scorelist)
            keywordCollections.append(keywordCollection)
            nmfDims.append(nmfDim[0])
        pass
        if n >1:
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
        elif n == 1:
            kw = self.container.keywords[-1]
            for i in range(len(keywordCollections)):
                kws = KeywordSuggestion(keywordCollections[i][0])
                kws.nmfDim = nmfDims[i]
                kw.suggestions.append(kws)

        PoemRepository.save(self.container)

        return self.container.to_dict()

    def get1Keyword(self):
        n = 0
        cntSyl = 0

        while True:
            kw = random.choice(self.i2w)
            n += 1
            cntSyl = count_syllables(kw)[1]

            if kw.isalpha() and ((kw not in self.inputKeywordsList) or (cntSyl < 3 or (n > 16 and cntSyl < 2))):
                break

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

