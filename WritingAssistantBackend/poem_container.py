import re # Regular expressions

from .poem_repository import SuggestionRepository

class BaseContainer():
    def __init__(self):
        self._id = None
        self._oldId = None

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, idValue):
        inValue = self.__format_Id__(idValue) if idValue is not None else None

        if self.id is not None and inValue is not None:
            if inValue != self._id:
                self._oldId = self._id
        self._id = inValue

    @property
    def oldId(self):
        return self._oldId

    @staticmethod
    def cleanupText(text):
        return re.sub(' +', ' ', text).strip()

    def __format_Id__(self, idValue):
        prefix = self.__class__.__name__[0].lower()
        if isinstance(idValue,(int,float)):
            inValue = idValue
        elif isinstance(idValue,(str)):
            if idValue.endswith("-tmp"):
                inValue = idValue
            else:
                inValue = idValue.replace(prefix + '-', '')
            if inValue.isnumeric():
                inValue = int(inValue)
        else:
            try:
                inValue = int(idValue)
            except:
                inValue = idValue
        return inValue


class Poem(BaseContainer):
    def __init__(self, id = None, poem_text: str = None, title: str = None, form=None, nmfDim=0, lang=None, status = 1):
        super().__init__()
        self._id = id
        self._title = title
        self._stanzas = []
        self._form = form
        self._nmfDim = nmfDim
        self._poemLanguage = lang
        self._status = status
        self._origin = None
        self._keywords = []
        # If the user has already written some text, there will be at least one stanza
        # Split the poem on \n\n into stanzas and add stanzas to the poem-object
        # If no text is given, create an empty poem object
        if poem_text:
            for s in poem_text.split("\n\n"):
                self.addStanza(stanzaText=s, order=len(self._stanzas))

    def addStanza(self, order=-1, id = None, stanzaText: str = None):
        st_order = order if order >= 0 else len(self._stanzas)
        self._stanzas.append(Stanza(stanzaText=stanzaText, order=st_order, id=id))

    def receiveUserInput(self, userInput, structure, title=None):
        if title is not None: self.title = title
        if not userInput: # if there's no user input, we can skip this
            return False
        stanzas = structure["struct-sandbox"].split(',')
        for s in stanzas:
            hasVerse = False
            for vw in structure["struct-"+s].split(','):
                hasVerse = True
                break
            if hasVerse:
                self._stanzas.append(Stanza(id=s, userInput=userInput, structure=structure))

    @property
    def form(self):
        return self._form

    @form.setter
    def form(self, value):
        self._form = value

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self,title):
        self._title = title

    @property
    def language(self):
        return self._poemLanguage

    @language.setter
    def language(self, value):
        self._poemLanguage = value

    @property
    def nmfDim(self):
        return self._nmfDim

    @nmfDim.setter
    def nmfDim(self, value):
        self._nmfDim = value

    @property
    def status(self):
        return self._status
    @status.setter
    def status(self,value):
        self._status = value

    @property
    def stanzas(self):
        return list(self._stanzas)

    @property
    def origin(self):
        return self._origin
    @origin.setter
    def origin(self, value):
        self._origin = value

    @property
    def keywords(self):
        return self._keywords

    def blacklists(self):
        # titleWords = [w.lower() for w in self.title.split(" ")] if self.title else []
        rhyme = []
        words = set()
        for s in self.stanzas:
            BL = s.blacklists()
            # rhyme.extend([w for w in BL["rhyme"] if not w in titleWords])
            # words.update([w for w in BL["words"] if not w in titleWords])
            rhyme.extend([w for w in BL["rhyme"]])
            words.update([w for w in BL["words"]])
        return {"rhyme": rhyme, "words": words}

    def to_dict(self):
        # Return a dictionary representation of the poem, containing stanzas
        pass
        poem = {
            "parameters": {
                "form": self.form,
                "nmfDim": self.nmfDim
            },
            "stanzas": [s.to_dict() for s in self.stanzas]
        }
        if self.id is not None: poem["id"] = self._id
        if self.oldId is not None: poem["oldId"] = self._oldId
        if self.title is not None: poem["title"] = self._title
        if self.status is not None: poem["status"] = self._status
        if self.keywords is not None: poem["keywords"] = [k.to_dict() for k in self.keywords]
        return poem


class Stanza(BaseContainer):
    def __init__(self, order=0, stanzaText: str = None, id = None, structure = None, userInput = None):
        super().__init__()
        self._verses = []
        self._order = order
        self._id = self.__format_Id__(id)
        # If the user has already written some text, there will be at least one stanza
        # Split the stanza on \n into verses and add verses to the stanza-object
        # If no text is given, there will be no stanza object
        if stanzaText:
            for v in stanzaText.splitlines():
                self.addVerse(verseText=v, order=len(self._verses))
        # If a structure is defined, it means we have to store user input in the poem container
        if structure is not None:
            self.id = self.__format_Id__(id)
            for key in structure.keys():
                if key == "struct-"+id:
                    for v in structure[key].split(','):
                        if not v.startswith("suggB"):
                            vTxt = userInput[structure["struct-"+v]]
                            self.addVerse(id = structure["struct-"+v], verseText=vTxt)

    def addVerse(self, order=-1, verseText: str = None, id = None):
        v_order = order if order >= 0 else len(self._verses)
        self._verses.append(Verse(id=id, verseText=verseText, order=v_order))

    @property
    def verses(self):
        return list(self._verses)

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        self._order = value

    def blacklists(self):
        words = set()
        rhyme = []
        for v in self.verses:
            BL = v.blacklists()
            rhyme.extend(BL["rhyme"])
            if BL["words"] is not None: # do not try to append if the verse is empty
                words.update(BL["words"])
        return {"rhyme": rhyme, "words": words}

    def to_dict(self):
        # Return a dictionary representation of the stanza
        stanza = {
            "verses": [v.to_dict() for v in self.verses]
        }
        if self.id is not None: stanza["id"] = self._id
        if self.oldId is not None: stanza["oldId"] = self._oldId
        return {"stanza": stanza}


class Verse(BaseContainer):
    def __init__(self, order=0, verseText: str = None, id= None):
        super().__init__()
        if isinstance(verseText,(str)):
            self._suggestions = None
            self._words = self.cleanupText(verseText) or ""
        else:
            self._suggestions = [Suggestion(text=txt) for txt in verseText]
            self._words = ""
        self._order = order
        self.id = id

    @property
    def suggestions(self):
        return self._suggestions
    @suggestions.setter
    def suggestions(self, value):
        if isinstance(value, list):
            self._suggestions = [Suggestion(text=s) for s in value]
        else:
            self._suggestions = [Suggestion(text=value)]

    @property
    def text(self):
        return self._words

    @text.setter
    def text(self, value):
        _words = self.cleanupText(value) or ""

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        self._order = value

    def blacklists(self):
        words = set()
        rhyme = []
        filteredText = re.sub(r"(?:[^\w\s]|_)+", '', self.text) #filter out non-alphanumeric characters
        wordsList = [w for w in filteredText.split(" ") if w != ""]
        if len(wordsList) > 0 : rhyme.extend([wordsList[-1].lower()])
        words.update([w.lower() for w in wordsList])

        if self.text == "":
            previousSugg = SuggestionRepository.lookupSuggestionsByVerse(self.id)
            if not previousSugg is None:
                for sugg in previousSugg:
                    filteredText = re.sub(r"(?:[^\w\s]|_)+", '',sugg["suggestion"])  # filter out non-alphanumeric characters
                    wordsList = filteredText.split(" ")
                    rhyme.extend([wordsList[-1]])
                    words.update([w.lower() for w in wordsList])

        return {"rhyme": rhyme, "words": words}

    def to_dict(self):
        verse = {
            "text": self._words
        }
        if self.id is not None: verse["id"] = self._id
        if self._oldId is not None: verse["oldId"] = self._oldId
        if self._suggestions is not None:
            verse["suggestions"] = [s.to_dict() for s in self._suggestions]
        return {"verse": verse}
    
class Suggestion(BaseContainer):
    def __init__(self, text: str = None, id = None):
        super().__init__()
        self._words = self.cleanupText(text) or ""
        self.id = id
        self.batchId = None

    @property
    def text(self):
        return self._words
    @text.setter
    def text(self, value):
        self._words = self.cleanupText(value) or ""

    @property
    def batchId(self):
        return self._batchId
    @batchId.setter
    def batchId(self, value):
        self._batchId = value

    def to_dict(self):
        suggestion = {
            "text": self._words
        }
        if self.id is not None: suggestion["id"] = self.id
        if self.batchId is not None: suggestion["batchId"] = self.batchId
        return {"suggestion": suggestion}

class Keyword(BaseContainer):
    def __init__(self, text: str = None, id = None):
        super().__init__()
        self._text = self.cleanupText(text) or ""
        self._id = id
        self._suggestions = []

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = self.__format_Id__(value) if value is not None else None
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, value):
        self._text = self.cleanupText(value) or ""
    @property
    def suggestions(self):
        return self._suggestions

    def to_dict(self):
        keyword = {
            "text": self._text
        }
        if self.id is not None: keyword["id"] = self.id
        if len(self._suggestions) > 0:
            collections = {}
            keyword["suggestions"] = [s.to_dict() for s in self._suggestions]
        return keyword

class KeywordSuggestion(BaseContainer):
    def __init__(self, suggestion = None, id = None):
        super().__init__()
        self._suggestion = suggestion
        self.id = id
        self.batchId = None

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = self.__format_Id__(value) if value is not None else None
    @property
    def collectionId(self):
        return self._collectionId
    @collectionId.setter
    def collectionId(self, value):
        self._collectionId = value
    @property
    def suggestion(self):
        return self._suggestion
    @suggestion.setter
    def suggestion(self, value):
        self._suggestion = value

    def to_dict(self):
        suggestion = {
            "suggestion": self._suggestion
        }
        if self.id is not None: suggestion["id"] = self.id
        if self.collectionId is not None: suggestion["collectionId"] = self.collectionId
        return suggestion
