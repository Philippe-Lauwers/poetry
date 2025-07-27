#!/usr/bin/env python

import codecs
import copy
import os
import pickle
import random
import re
import sys, traceback
import time
import math
import warnings
from datetime import datetime

import kenlm
import numpy as np
import scipy.stats
# container to store the output in a hierarchy of Poem>>Stanza>>Verse>>Suggestion and Keyword>>KeywordSuggestion objects
from .poem_container import Poem as PoemContainer
from .poem_repository import PoemRepository
from .poembase_config import PoembaseConfig
from .poemutils import count_syllables, hmean
from .verse_generator import VerseGenerator

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
        self._rhymeCache = {} # cache for rhymes, to avoid repeated lookups in the rhyme dictionary

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

    def initPoemContainer(self, id=None, form=None,nmfDim=None, lang=None, title=None, origin=None):
        #Delete any lingering instances of the PoemBase class
        try:
            obj = self.container
            del obj
        except AttributeError:
            pass

        self.container = PoemContainer()
        if id is not None: self.container.id = id
        self.container.form = form
        self.container.title = title
        self.container.nmfDim = nmfDim
        self.container.language = lang
        self.container.origin = origin

    def receiveUserInput(self, id=None, title=None, form=None, nmfDim=None, userInput=None, structure=None):
        if nmfDim is None or nmfDim == 'random':
            # get the nmfDim: None if the argument is None, a random value if the argument is 'random'
            nmfDim = random.randint(0, self.W.shape[1] - 1)
        elif not isinstance(nmfDim, int):
            if nmfDim.isdigit():
                nmfDim = int(nmfDim)

        self.initPoemContainer(id=id, form=form, nmfDim=nmfDim, lang=self.lang, origin='browser', title=title)
        # Stores a representation of the poem in the database
        self.container.receiveUserInput(userInput, structure, title)

        PoemRepository.save(self.container)

    def write(self, constraints=('rhyme'), form='sonnet', nmfDim=None, userInput=None, structure=None, title=None, keywords=None):
        self.form = form
        self.blacklist_words = set()
        self.blacklist = []
        self.previous_sent = None
        self.keywords = keywords if keywords else []
        self._numVerses = 0

        if nmfDim is None or nmfDim == 'random':
            nmfDim = self.container.nmfDim

        if userInput is None:
            self.initPoemContainer(form=form, nmfDim=nmfDim, lang=self.lang, origin='GRU', title=None)

        if title is not None and title != '' and title != self.container.title:
            self.container.title = title

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
            # Rhyme forms
            rhymeForm = None
            for w in blacklists["rhyme"]:
                if w != "":
                    search_w = w
                    rhymeForm = None
                    # Lookup kw in the rhyme dictionary, drop first letter until a match is found or string is empty
                    while search_w:
                        rhymeForm = next((value for key, value in self.rhymeDictionary.items() if key.endswith(search_w)), None)
                        if rhymeForm:
                            break  # found a match
                        search_w = search_w[1:]
                if rhymeForm and rhymeForm not in self.blacklist:
                        self.blacklist.append(rhymeForm)
            # All words used
            self.blacklist_words = self.blacklist_words.union(blacklists["words"])

        if self.keywords:
            nmfDim = self.reevaluateNmfDim(title=self.container.title, keywords=self.keywords, userInput=userInput)
        else:
            nmfDim = self._nmfDim # the value that was stored at initialization of the PoemBase instance

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
                    tb_str = traceback.format_exc()
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
                        self.container.stanzas[-1].addVerse(verseText=' '.join(words)).capitalizeVerse()
                    else: # generating n suggestions when a single verse is requested
                        self.container.stanzas[-1].verses[-1].suggestions = [' '.join(w) for w in words]
                    # writes the generated verse to stdout and log
                    if isinstance(words[0], str):
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

        firstPart = []
        keyword = None
        try: # try to generate a part of the verse that ends with the keyword
            # for many keywords, data is too sparse to properly do this, resulting in key errors
            if self.keywords:
                allFirstPartCandidates = []
                allFirstPartScores = []
                allFirstPartEncDecScores = []

                # Attempt to spread the keywords evenly, slightly larger chance to pick a keyword
                if random.choices([True, False], weights=[len(self.keywords)+1,self._numVerses-1])[0]:
                    pickKeyword = 0
                else:
                    pickKeyword = len(self.keywords)
                while pickKeyword < len(self.keywords):
                    keyword = random.choice(list(self.keywords.values()))
                    if keyword in self._rhymeCache.values():
                        break
                    pickKeyword += 1
                if keyword != "" and keyword not in self.blacklist_words:
                    dfltMax_length = self.generator.maxLength
                    self.generator.maxLength = math.ceil(dfltMax_length / random.randint(4, 6))
                    dfltNBatches = self.generator.nBatchesDecoder
                    self.generator.nBatchesDecoder = math.ceil(4 + (dfltNBatches-4)*self.generator.maxLength/dfltMax_length)
                    # Generate a part of a verse that precedes the keyword
                    allFirstPartCandidates, allFirstProbScores = self.generator.generateCandidates(previous=previous, rhymePrior=self.createKeywordProbVector(keyword), nmfPrior=nmfPrior)
                    firstPartScoreList = self.scoreCandidates(allCandidates=allFirstPartCandidates, allProbScores=allFirstProbScores,nmf=nmf, syllables=syllables)
                    # Take the first candidate that contains the keyword (if in the first 12)
                    i = 0
                    while i < 12:
                        if keyword in firstPartScoreList[i][1]:
                            firstPart = firstPartScoreList[i][1]
                            break
                        i+= 1
                    if not firstPart:
                        #If keyword not found, take the best scoring candidate
                        firstPart = firstPartScoreList[0][1]

                    # Add that to the "previous" variable but drop the first len(firstPart) words
                    lenFirstPart = len(firstPart)
                    if previous:
                        previous = previous[lenFirstPart:] + firstPart
                    else:
                        previous = firstPart
                    # Determine how much of the verse still has to be generated + adapt number of batches accordingly
                    self.generator.maxLength = math.ceil((1 - lenFirstPart/self.generator.maxLength) * dfltMax_length)
                    self.generator.nBatchesDecoder = 0
        except: # If generating a first part fails, we can continue generating an entire verse
            # Before we do that, restore the defaults for maxLength and nBatchesDecoder
            tb_str = traceback.format_exc()
            pass
            self.generator.maxLength = 0
            self.generator.nBatchesDecoder = 0
            previous = self.previous_sent
        allCandidates, allProbScores = self.generator.generateCandidates(previous=previous,rhymePrior=rhymePrior, nmfPrior=nmfPrior)
        scoreList = self.scoreCandidates(allCandidates=allCandidates, allProbScores=allProbScores,nmf=nmf, syllables=syllables)

        # restore defaults (value = 0 means the setter in VerseGenerator will ste the values back to default)
        # ==> ready for the next verse
        self.generator.maxLength = 0
        self.generator.nBatchesDecoder = 0

        if n == 1:
            i = 0
            if keyword:
                while i < 12:
                    if firstPart:
                        output = firstPart + scoreList[i][1]
                    else:
                        output = scoreList[i][1]
                    if keyword in output:
                        break
                    i += 1
            if firstPart:
                output = firstPart + scoreList[0][1]
            else:
                output = scoreList[0][1]
        else:
            output = []
            pickedList = []
            if keyword:
                i = 0
                while i < 12 and len(output) < n:
                    if firstPart:
                        verse = firstPart + scoreList[i][1]
                    else:
                        verse = scoreList[i][1]
                    if keyword in verse:
                        output.append(verse)
                        pickedList.append(i)
                    i += 1
            randomList = self.pickRandomNfromN2(n, scoreList)
            i = 0
            while i < len(randomList) and len(output) < n:
                if i not in pickedList: # if the candidate was not already picked because of the keyword
                    if firstPart:
                        verse = firstPart + randomList[i][1]
                    else:
                        verse = randomList[i][1]
                output.append(verse)
                i += 1
        return output

    def scoreCandidates(self, allCandidates=None, allProbScores=None, nmf=None, syllables=None):
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

        return scoreList

    def pickRandomNfromN2(self, n, listIn):
        N2_topped = min(n**2,12) # no testing required, list contains >> 12 elements/anything beyond 12 is not useful
        N2_list = listIn[:N2_topped]
        listOut = random.sample(N2_list, n)
        return listOut

    def reevaluateNmfDim(self, title=None, keywords=None, userInput=None):
        # If all arguments are empty, stick to the current nmfDim
        if title is None and keywords is None and userInput is None:
            return self._nmfDim

        titleWords = title.split(' ') if title else []
        keywordsList = [keyword.lower() for keyword in keywords.values()] if keywords else []
        inputWordsList =  [word.lower()
                        for sentence in userInput.values() if sentence.strip()
                        for word in re.sub(r"[^\w\s]", "", sentence).split()
                        ] if userInput else []

        nmfDim = (0, 0)
        for i in range(len(self.nmf_descriptions)):
            nmfScore = self.checkNMF(list(set(titleWords) | set(keywordsList) | set(inputWordsList)), [i])
            if nmfScore > nmfDim[1]:
                scorelist = list(nmfDim)
                scorelist[0] = i
                scorelist[1] = nmfScore
                nmfDim = tuple(scorelist)
        self.container.nmfDim = nmfDim[0]
        self._nmfDim = nmfDim[0]
        return nmfDim[0]


    def getRhymeStructure(self, cutoff=10, userInput=None):
        if userInput is None:
            return self.getCompleteRhymeStructure(cutoff=cutoff)
        else:
            return self.get1VerseRhymeStructure(cutoff=cutoff, userInput=userInput)

    def getCompleteRhymeStructure(self, cutoff=10):
        chosenList = []
        mapDict = {}

        structure = PoembaseConfig.Poemforms.getElements(form=self.form, lang=self.lang)

        # Store the number of verses for future use
        poemStructureVerses = ()  # re-create the tuple without the empty lines (to match the user input)
        for el in structure:
            if el != '':
                poemStructureVerses += (el,)
        # Store the number of verses for future use
        self._numVerses = len(poemStructureVerses)

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
        # Store the number of verses for future use
        self._numVerses = len(poemStructureVerses)

        userInputLastWords = []
        if userInput:
            for k in userInput.keys():
                userInputLastWords.append(self.cleanInputVerse(userInput[k])[-1])

        if userInput:
            for i in range(len(userInputLastWords)): # this is the location of the verse we want to generate
                # if there is text for this verse, there is a last word and thus rhyme
                # if not, we pick a random rhyme
                if userInputLastWords[i] == '':
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
        # 1. Determine (randomly) whether we pick a random rhyme or one of the keywords
        pickKeyword = random.choice([True, False]) if self.keywords else False
        # 2. If we pick a keyword, we will look for a rhyme that matches the keyword
        if pickKeyword and pickKeyword not in self._rhymeCache.values():
            rhymeDict = {}
            for kw in self.keywords.values():
                if kw not in self.blacklist_words:
                    search_kw = kw
                    rhymeForm = None
                    # Lookup kw in the rhyme dictionary, drop first letter until a match is found or string is empty
                    while search_kw:
                        rhymeForm =  next((value for key, value in self.rhymeDictionary.items() if key.endswith(search_kw)), None)
                        if rhymeForm:
                            search_kw = kw # set back to the original keyword for later use
                            break  # found a match
                        search_kw = search_kw[1:]
                    # If found, we store it in a dictionary with its frequency
                    if rhymeForm:
                        if rhymeForm not in self.blacklist:
                            if rhymeForm[-1] in self.freqRhyme and self.freqRhyme[rhymeForm[-1]] >= cutoff:
                                if rhymeForm[-1] not in rhymeDict:
                                    rhymeDict[rhymeForm[-1]] = self.freqRhyme[rhymeForm[-1]]
                                else: # if the rhymeForm is already in the dictionary, we randomly decide whether to replace
                                    if(random.choice([True, False])):
                                        rhymeDict[rhymeForm[-1]] = self.freqRhyme[rhymeForm[-1]]
            if rhymeDict:
                rhymeDictByFreq = {v: k for k, v in rhymeDict.items()}
                # If we found the rhymes mathing the keywords, we pick randomly
                # with a higher chance for the more frequent rhymes
                freqs = sorted(rhymeDict.values(), reverse=True)
                weightedFreqs = []
                while freqs:
                    weightedFreqs.extend(freqs)
                    freqs.pop()
                chosenFreq = random.choice(list(set(weightedFreqs)))
                if search_kw in self.rhymeDictionary:
                    self._rhymeCache[rhymeForm[-1]] = search_kw
                return rhymeDictByFreq[chosenFreq]
        # 3. If we did not pick a keyword or no appropriate rhyme is found,
        #    we will randomly select a rhyme from the rhyme dictionary
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
        if self._rhymeCache:
            # There is a rhyme cache when we created rhymes from keywords
            # -> maximum rhyme probabilities for the chosen keyword
            if rhyme in self._rhymeCache.keys():
                probVector[self.w2i[self._rhymeCache[rhyme]]] = 1
                return probVector / np.sum(probVector)
        else:
            for w in self.rhymeInvDictionary[rhyme]:
                if not self.rhymeDictionary[w] in self.blacklist and not w in self.blacklist_words:
                    probVector[self.w2i[w]] = 1

        return probVector / np.sum(probVector)

    def createKeywordProbVector(self, keyword):
        probVector = np.empty(len(self.i2w))
        probVector.fill(1e-20)

        if keyword in self.rhymeDictionary:
            kwRhyme = self.rhymeDictionary[keyword]
            if kwRhyme:
                # If the keyword is in the rhyme dictionary
                # -> only probabilities for the chosen keyword
                probVector[self.w2i[keyword]] = 1
                return probVector / np.sum(probVector)
            else:
                return None
        else:
            # If the keyword is not in the rhyme dictionary, we look for a rhyme that matches the keyword
            # by dropping the first letter until a match is found or the string is empty
            searchKW = keyword
            while searchKW:
                if searchKW in self.rhymeDictionary:
                    kwRhyme = self.rhymeDictionary[searchKW]
                    break
                searchKW = searchKW[1:]
            if kwRhyme:
                # if a rhyme is found for a keyword not in the rhyme dictionary,
                # set probabilities for all words that rhyme with the keyword
                if kwRhyme in self.rhymeInvDictionary:
                    for w in self.rhymeInvDictionary[kwRhyme]:
                        if not w in self.blacklist_words:
                            probVector[self.w2i[w]] = 1
                return probVector / np.sum(probVector)
            else:
                return None


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
