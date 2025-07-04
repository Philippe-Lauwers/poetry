class BaseContainer():
    def __init__(self):
        self._id = None
        self._oldId = None
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, idValue):
        if self._id is not None:
            self._oldId = self._id
        self._id = idValue


class Poem(BaseContainer):
    def __init__(self, poem_text: str = None):
        super().__init__()
        self._stanzas = []
        self._form = None
        self._nmfDim = None
        self._poemLanguage = 1
        # If the user has already written some text, there will be at least one stanza
        # Split the poem on \n\n into stanzas and add stanzas to the poem-object
        # If no text is given, create an empty poem object
        if poem_text:
            for s in poem_text.split("\n\n"):
                self.addStanza(stanzaText=s, order=len(self._stanzas))

    def addStanza(self, order=-1, stanzaText: str = None):
        st_order = order if order >= 0 else len(self._stanzas)
        self._stanzas.append(Stanza(stanzaText=stanzaText, order=st_order))

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
        if self._id is not None: poem["id"] = self._id
        if self._oldId is not None: poem["oldId"] = self._oldId
        return poem


class Stanza(BaseContainer):
    def __init__(self, order=0, stanzaText: str = None):
        super().__init__()
        self._verses = []
        self._order = order
        pass
        # If the user has already written some text, there will be at least one stanza
        # Split the stanza on \n into verses and add verses to the stanza-object
        # If no text is given, there will be no stanza object
        if stanzaText:
            for v in stanzaText.splitlines():
                self.addVerse(verseText=v, order=len(self._verses))

    def addVerse(self, order=-1, verseText: str = None):
        v_order = order if order >= 0 else len(self._verses)
        self._verses.append(Verse(verseText=verseText, order=v_order))

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
        if self._oldId is not None: stanza["oldId"] = self._oldId
        return {"stanza": stanza}

class Verse(BaseContainer):
    words = None

    def __init__(self, order=0, verseText: str = None):
        super().__init__()
        self._words = verseText or ""
        self._order = order

    @property
    def text(self):
        return self._words

    @text.setter
    def text(self, value):
        _words = value

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
