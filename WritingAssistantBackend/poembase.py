#!/usr/bin/env python

import sys
import random
#from countsyl import count_syllables
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
from pprint import pprint
import onmt
import argparse
import torch
import json
import warnings

from .verse_generator import VerseGenerator
from .poem_container import Poem as PoemContainer, Stanza, Verse # container to store the output in a hierarchy of Poem>>Stanza>>Verse objects
from .poembase_config import PoembaseConfig
from .poem_repository import PoemRepository, StanzaRepository, VerseRepository

warnings.filterwarnings("ignore")

class PoemBase:

    def __init__(self, lang):

        self.lang = lang # store the language for this instance of the PoemBase class

        self.initializeConfig(lang)
        self.loadRhymeDictionary()
        self.loadNMFData()

        self.generator = VerseGenerator(self.MODEL_FILE, self.entropy_threshold)
    
        self.loadVocabulary()

        self.ngramModel = kenlm.Model(self.NGRAM_FILE)

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

    def initializeConfig(self, lang):

        """with open(config) as json_config_file:
            configData = json.load(json_config_file)"""
        
        location = os.path.join(
            PoembaseConfig.getParameter(category='general', parameterName='data_directory', language=lang),
            PoembaseConfig.getParameter(category='general', parameterName='language', language=lang)
        )
            
        self.NMF_FILE = os.path.join(location, PoembaseConfig.getParameter(category='nmf', parameterName='matrix_file', language=lang))
        self.NMF_DESCRIPTION_FILE = os.path.join(location, PoembaseConfig.getParameter(category='nmf', parameterName='description_file', language=lang))
        self.RHYME_FREQ_FILE = os.path.join(location, PoembaseConfig.getParameter(category='rhyme', parameterName='freq_file', language=lang))
        self.RHYME_DICT_FILE = os.path.join(location, PoembaseConfig.getParameter(category='rhyme', parameterName='rhyme_dict_file', language=lang))
        self.RHYME_INV_DICT_FILE = os.path.join(location, PoembaseConfig.getParameter(category='rhyme', parameterName='rhyme_inv_dict_file', language=lang))
        self.MODEL_FILE = os.path.join(location, PoembaseConfig.getParameter(category='model', parameterName='parameter_file', language=lang))
        self.NGRAM_FILE = os.path.join(location, PoembaseConfig.getParameter(category='model', parameterName='ngram_file', language=lang))
        
        self.name = PoembaseConfig.getParameter(category='general', parameterName='name', language=lang)
        self.length = int(PoembaseConfig.getParameter(category='poem', parameterName='length', language=lang))
        self.entropy_threshold = float(PoembaseConfig.getParameter(category='poem', parameterName='entropy_threshold', language=lang))
        self.suggestionBatchSize = int(PoembaseConfig.getParameter(category='poem', parameterName='suggestion_batch_size', language=lang))

    def loadNMFData(self):
        self.W = np.load(self.NMF_FILE)
        with open(self.NMF_DESCRIPTION_FILE, 'rb') as f:
            self.nmf_descriptions = pickle.load(f, encoding='utf8')
        
    def loadRhymeDictionary(self):
        freqRhyme = {}
        with codecs.open(self.RHYME_FREQ_FILE, 'r', encoding='utf8') as f:
            for line in f:
                line = line.rstrip()
                rhyme, freq = line.split('\t')
                freqRhyme[rhyme] = int(freq)
        self.freqRhyme = freqRhyme
        self.rhymeDictionary = pickle.load(open(self.RHYME_DICT_FILE, 'rb'))
        self.rhymeInvDictionary = pickle.load(open(self.RHYME_INV_DICT_FILE, 'rb'))

    def loadVocabulary(self):
        self.i2w = self.generator.vocab.itos
        self.w2i = self.generator.vocab.stoi

    def initPoemContainer(self,form=None,nmfDim=None, lang=None, title=None, origin=None):
        #Delete any lingering instances of the PoemBase class
        try:
            obj = self.container
            del obj
        except AttributeError:
            pass
        # get the nmfDim: None if the argument is None, a random value if the argument is 'random'
        if nmfDim == 'random':
            self._nmfDim = random.randint(0, self.W.shape[1] - 1)
        elif type(nmfDim) == int:
            self._nmfDim  = nmfDim
        else:
            self._nmfDim = nmfDim

        self.container = PoemContainer()
        self.container.form = form
        self.container.title = title
        self.container.nmfDim = self._nmfDim
        self.container.language = lang
        self.container.origin = origin

    def receiveUserInput(self, title=None, form=None, nmfDim=None, userInput=None, structure=None):
        self.initPoemContainer(form=form, nmfDim=nmfDim, lang=self.lang, origin='browser', title=title)
        # Stores a representation of the poem in the database
        self.container.receiveUserInput(userInput, structure, title)
        PoemRepository.save(self.container)

    def write(self, constraints=('rhyme'), form='sonnet', nmfDim=False, userInput=None, structure=None, title=None):
        self.form = form
        self.blacklist_words = set()
        self.blacklist = []
        self.previous_sent = None

        if userInput is None:
            self.initPoemContainer(form=form, nmfDim=nmfDim, lang=self.lang, origin='GRU', title=None)

        if constraints == ('rhyme'):
            self.writeRhyme(nmfDim, userInput, structure)
        pass

    def writeRhyme(self, nmfDim, userInput=None, structure=None):
        # Flag to indicate whether a new stanza should be added,
        # set to true when a ' ' is encountered in the rhyme structure
        addNewStanza = False

        # Little trick: by generating the rhymeStructure one verse further than the user input, we generate one verse
        # If there is no user input, a complete draft will be generated
        rhymeStructure = self.getRhymeStructure(userInput=userInput)
        # If there is user input, we feed the last sentence of the input to the model
        if userInput is not None:
            i = -1
            while abs(i) < len(userInput) and list(userInput.values())[i] == '': # look for the last non-empty verse
                i -= 1
            if len(userInput.values()) > 0:
                self.previous_sent = self.cleanInputVerse(list(userInput.values())[i])
            blacklists = self.container.blacklists()
            self.blacklist.append([self.rhymeDictionary[w] for w in blacklists["rhyme"] if w != ""])
            self.blacklist_words = self.blacklist_words.union(blacklists["words"])
            pass
        nmfDim = self._nmfDim

        if not nmfDim == None:
            sys.stdout.write('\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +' nmfdim ' + str(nmfDim) + ' (' + ', '.join(self.nmf_descriptions[nmfDim]) + ')\n\n')
            self.log.write('\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' nmfdim ' + str(nmfDim) + ' (' + ', '.join(self.nmf_descriptions[nmfDim]) + ')\n\n')
        else:
            sys.stdout.write('\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' NO nmfdim' + '\n\n')
            self.log.write('\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' NO nmfdim' + '\n\n')
        for el in rhymeStructure:
            if el:
                try:
                    if userInput is not None:
                        nSuggestions = self.suggestionBatchSize
                    else:
                        nSuggestions = 1
                    words = self.getSentence(rhyme=el, syllables = True, nmf=nmfDim, n = nSuggestions)
                except KeyError as e:
                    print('err', e)
                    continue
                else:
                    # adds the generated text to the _poemContainer
                    if not self.container.stanzas or addNewStanza:
                        # If there is no stanza yet
                        #   or a ' ' was encountered in the rhyme structure before generating the verse
                        # -> add a new stanza to the _poemContainer
                        # If there is user input, fetch the id of the last stanza from the structure fields
                        # if userInput is not None:
                        #     stanzaID = structure['struct-sandbox'].split(',')[-1]
                        #     self.container.addStanza(id=stanzaID)
                        if userInput is None:
                            self.container.addStanza()
                        addNewStanza = False
                    if nSuggestions == 1: # generating a complete poem: only one suggestion is generated
                        self.container.stanzas[-1].addVerse(verseText=' '.join(words))
                    else: # generating n suggestions when a single verse is requested
                        self.container.stanzas[-1].verses[-1].suggestions = [' '.join(w) for w in words]
                    # writes the generated verse to stdout and log
                    if isinstance(words, str):
                        sys.stdout.write(' '.join(words) + '\n')
                        self.log.write(' '.join(words) + '\n')
                    else:
                        sys.stdout.write('Generated ' + str(nSuggestions) + ' suggestions' + '\n')
                        self.log.write('Generated ' + str(nSuggestions) + ' suggestions' + '\n')
                        for w in words:
                            sys.stdout.write(' '.join(w) + '\n')
                            self.log.write(' '.join(w) + '\n')
                    try:
                        if isinstance(words[0], list):
                            for verseWords in words:
                                self.blacklist.extend(self.rhymeDictionary[verseWords[-1]])
                                self.blacklist_words = self.blacklist_words.union(verseWords)
                        else:
                            self.blacklist.append(self.rhymeDictionary[words[-1]])
                            self.blacklist_words = self.blacklist_words.union(words)
                    except KeyError as e:
                        #means verse does not follow rhyme, probably because of entropy computations
                        #do not show error for presentation
                        print('err blacklist', e)
                        pass
                    except IndexError as e2:
                        print('err blacklist index', e2)
                    self.previous_sent = words
            else:
                # Writes an empty line for a ' ' in the rhyme structure
                addNewStanza = True
                sys.stdout.write('\n')
                self.log.write('\n')
        # self.signature()
        self.log.write('\n\n')
        self.log.flush()

    def getSentence(self, rhyme, syllables, nmf, n=3):
        if self.previous_sent:
            previous = self.previous_sent
        else:
            previous = None
        if rhyme:
            rhymePrior = self.createRhymeProbVector(rhyme)
        else:
            rhymePrior = None
        if not nmf == None:
            nmfPrior = copy.deepcopy(self.W[:,nmf])
        else:
            nmfPrior = None

        allCandidates = []
        allProbScores = []
        allEncDecScores = []

        allCandidates, allProbScores = self.generator.generateCandidates(previous=previous,rhymePrior=rhymePrior, nmfPrior=nmfPrior)
        ngramScores = []
        for ncand, candidate in enumerate(allCandidates):
            try:
                ngramScore = self.ngramModel.score(' '.join(candidate)) / len(candidate)
            except ZeroDivisionError:
                ngramScore = -100
            ngramScores.append(ngramScore)
        ngramScores = np.array(ngramScores)
        largest = ngramScores[np.argmax(ngramScores)]
        ngramNorm = np.exp(ngramScores - largest)

        allProbScores = np.array([i.cpu().detach().numpy() for i in allProbScores])
        largest = allProbScores[np.argmax(allProbScores)]
        allProbNorm = np.exp(allProbScores - largest)

        scoreList = []
        for ncand, candidate in enumerate(allCandidates):
            allScores = [allProbNorm[ncand], ngramNorm[ncand]]
            if syllables:
                syllablesScore = self.checkSyllablesScore(candidate, mean=self.length, std=2)
                allScores.append(syllablesScore)
            if nmf:
                NMFScore = self.checkNMF(candidate, [nmf])
                allScores.append(NMFScore)
            allScore = hmean(allScores)
            scoreList.append((allScore, candidate, allScores))

        scoreList.sort()
        scoreList.reverse()
        if n == 1:
            output = scoreList[0][1]
        else:
            randomList = self.pickRandomNfromN2(n, scoreList)
            output = []
            for i in range(n):
                output.append(randomList[i][1])

        return output

    def pickRandomNfromN2(self, n, listIn):
        N2_topped = min(n**2,12) # no testing required, list contains >> 12 elements
        N2_list = listIn[:N2_topped]
        listOut = random.sample(N2_list, n)
        return listOut


    def getRhymeStructure(self, cutoff=10, userInput=None):
        if userInput is None:
            return self.getCompleteRhymeStructure(cutoff=cutoff)
        else:
            return self.get1VerseRhymeStructure(cutoff=cutoff, userInput=userInput)

    def getCompleteRhymeStructure(self, cutoff=10):
        chosenList = []
        mapDict = {}

        structure = PoembaseConfig.Poemforms.getElements(form=self.form, lang=self.lang)
        for el in set(structure):
            if not el in mapDict:
                if el != '':
                    randomSample = self.randomRhymeSample(cutoff=cutoff, chosenList=chosenList)
                    mapDict[el] = randomSample
                    chosenList.append(randomSample)
                else:
                    mapDict[el] = ''

        rhymeStructure = []
        for structEl in structure:
            if structEl:
                rhymeStructure.append(mapDict[structEl])
            else:
                rhymeStructure.append(structEl)
        return rhymeStructure

    def get1VerseRhymeStructure(self, cutoff=10, userInput=None):
        # Based on the userInput and the chosen form of the poem, this functions chooses an end sound for the next verse.
        # By generating only a sound for the next verse, we will limit the model to generating only one verse, no further
        # 'magic' will be required to curb the model.
        chosenList = []
        mapDict = {}

        # Created a tuple that contains the rhyme pattern without the blanks for easier looping afterwards
        poemStructure = PoembaseConfig.Poemforms.getElements(form=self.form, lang=self.lang)
        poemStructureVerses = () # re-create the tuple without the empty lines (to match the user input)
        for el in poemStructure:
            if el != '':
                poemStructureVerses += (el,)
        userInputLastWords = []
        if userInput:
            for k in userInput.keys():
                userInputLastWords.append(self.cleanInputVerse(userInput[k])[-1])

        if userInput:
            for i in range(len(userInputLastWords)):
                if userInputLastWords[i] == '': # this is the location of the verse we want to generate
                    if not poemStructureVerses[i] in mapDict:
                        randomSample = self.randomRhymeSample(cutoff=cutoff, chosenList=chosenList)
                        mapDict[poemStructureVerses[i]] = randomSample
                        chosenList.append(randomSample)
                    # else: # We know which rhyme applies to this verse, we don't have to look for one
                        # pass
                else: # if userInputLastWords[i] != '':
                    if not poemStructureVerses[i] in mapDict:
                        try:
                            rhymeEnding = self.rhymeDictionary[userInputLastWords[i]][-1]
                            mapDict[poemStructureVerses[i]] = rhymeEnding
                            chosenList.append(rhymeEnding)
                        except KeyError: # replace by lookup with more blablabla if there is time
                            randomSample = self.randomRhymeSample(cutoff=cutoff, chosenList=chosenList)
                            mapDict[poemStructureVerses[i]] = randomSample
                            chosenList.append(randomSample)
        else: # if the user input is an empty dict (we know we requested suggestions, not an entire poem)
            randomSample = self.randomRhymeSample(cutoff=cutoff, chosenList=chosenList)
            # we have not received any user input, we use the first element in the rhyme scheme
            mapDict[poemStructureVerses[0]] = randomSample
            chosenList.append(randomSample)

        nEmpties = 0
        if len(userInputLastWords) == 0:
            return [mapDict[poemStructure[0]]]
        for i in range(len(userInputLastWords)):
            if poemStructure[i+nEmpties] == '': 
                nEmpties+= 1
            if userInputLastWords[i] == '':
                requestedVerse = [mapDict[poemStructure[i+nEmpties]]]
                # Check if the requested verse is preceded by an empty line in the poem structure (= new stanza)
                # If so, insert an empty string in the requested verse list
                if poemStructure[i+nEmpties-1] == '':
                    requestedVerse.insert(0, '')
                return requestedVerse

    def randomRhymeSample(self, cutoff=10, chosenList=None):
        freq = -1
        while (freq < cutoff) or rhymeForm in chosenList:
            rhymeForm = random.choice(list(self.freqRhyme.keys()))
            freq = self.freqRhyme[rhymeForm]
        return rhymeForm

    def cleanInputVerse(self, txt):
        return re.sub(r'[^\w\s]', '', txt).strip().split(' ')

    def createRhymeProbVector(self, rhyme):
        probVector = np.empty(len(self.i2w))
        probVector.fill(1e-20)
        for w in self.rhymeInvDictionary[rhyme]:
            if not self.rhymeDictionary[w] in self.blacklist:
                probVector[self.w2i[w]] = 1
        return probVector / np.sum(probVector)

    def signature(self):
        sys.stdout.write('\n                                     ')
        time.sleep(4)
        for el in '- ' + self.name:
            nap = random.uniform(0.1,0.6)
            sys.stdout.write(el)
            sys.stdout.flush()
            time.sleep(nap)
        sys.stdout.write('\n')

    def typeString(self, verse):
        for el in verse:
            nap = random.uniform(0.1,0.3)
            sys.stdout.write(el)
            sys.stdout.flush()
            time.sleep(nap)
        return None


    def checkSyllablesScore(self, words, mean, std):
        gaussian = scipy.stats.norm(mean,std)
        nSyllables = sum([count_syllables(w)[1] for w in words])
        return gaussian.pdf(nSyllables) / 0.19

    def computeNMFScore(self,words,dimList):
        sm = 0
        sm = sum([max(self.W[self.w2i[w],dimList]) for w in words if w in self.w2i])
        return sm

    def checkNMF(self, words, dimList):
        words = list(set([w for w in words if not w in self.blacklist_words]))
        NMFTop = np.max(np.max(self.W[:,dimList], axis=0))
        NMFScore = self.computeNMFScore(words, dimList)
        return NMFScore / NMFTop

    # For retaining an instance of PoemBase in cache (for each server process)
    _poembase_instance = None
    def get_poembase(self, form,config):
        #returns a PoemBase object, creating one if necessary
        global _poembase_instance
        if _poembase_instance is None:
            _poembase_instance = PoemBase(form, config)
        return self
