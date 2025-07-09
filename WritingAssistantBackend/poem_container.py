import re # Regular expressions

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
    def __init__(self, poem_text: str = None, form=None, nmfDim=None, lang=None):
        super().__init__()
        self._stanzas = []
        self._form = form
        self._nmfDim = nmfDim
        self._poemLanguage = lang
        # If the user has already written some text, there will be at least one stanza
        # Split the poem on \n\n into stanzas and add stanzas to the poem-object
        # If no text is given, create an empty poem object
        if poem_text:
            for s in poem_text.split("\n\n"):
                self.addStanza(stanzaText=s, order=len(self._stanzas))

    def addStanza(self, order=-1, id = None, stanzaText: str = None):
        st_order = order if order >= 0 else len(self._stanzas)
        self._stanzas.append(Stanza(stanzaText=stanzaText, order=st_order, id=id))

    def receiveUserInput(self, userInput, structure):
        stanzas = structure["struct-sandbox"].split(',')
        for s in stanzas:
            hasVerse = False
            for vw in structure["struct-"+s].split(','):
                v = structure["struct-"+vw]
                if userInput[v] != "":
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
    def stanzas(self):
        return list(self._stanzas)

    @property
    def origin(self):
        return self._origin
    @origin.setter
    def origin(self, value):
        self._origin = value

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
        return poem


class Stanza(BaseContainer):
    def __init__(self, order=0, stanzaText: str = None, id = None, structure = None, userInput = None):
        super().__init__()
        self._verses = []
        self._order = order
        self._id = self.__format_Id__(id)
        pass
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
                        vTxt = userInput[structure["struct-"+v]]
                        if vTxt != "":
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

    def to_dict(self):
        # Return a dictionary representation of the stanza
        stanza = {
            "verses": [v.to_dict() for v in self.verses]
        }
        if self.id is not None: stanza["id"] = self._id
        if self.oldId is not None: stanza["oldId"] = self._oldId
        return {"stanza": stanza}

class Verse(BaseContainer):
    words = None

    def __init__(self, order=0, verseText: str = None, id= None):
        super().__init__()
        self._words = self.cleanupText(verseText) or ""
        self._order = order
        self.id = id

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

    def to_dict(self):
        verse = {
            "text": self._words
        }
        if self._id is not None: verse["id"] = self._id
        if self._oldId is not None: verse["oldId"] = self._oldId
        return {"verse": verse}
