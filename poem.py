class Poem:
    def __init__(self, poem_text: str=None):
        self._stanzas = []
        self._form = None
        self._nmfDim = None
        # If the user has already written some text, there ill be at least one stanza
        # Split the poem on \n\n into stanzas and add stanzas to the poem-object
        # If no text is given, create an empty poem object
        if poem_text:
            for s in poem_text.split("\n\n"):
                self.addStanza(s)

    def addStanza(self, stanza_text: str=None):
        self._stanzas.append(Stanza(stanza_text))

    @property
    def form(self):
        return self._form
    @form.setter
    def form(self,value):
        self._form = value

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
        return {
            "parameters": {
                "form": self.form,
                "nmfDim": self.nmfDim
            },
            "stanzas": [s.to_dict() for s in self.stanzas]
        }


class Stanza:
    def __init__(self, stanzaText: str=None):
        self._verses = []
        pass
        # If the user has already written some text, there will be at least one stanza
        # Split the stanza on \n into verses and add verses to the stanza-object
        # If no text is given, there will be no stanza object
        if stanzaText:
            for v in stanzaText.splitlines():
                self.addVerse(v)

    def addVerse(self, verse_text: str):
        self._verses.append(Verse(verse_text))

    @property
    def verses(self):
        return list(self._verses)

    def to_dict(self):
        # Return a dictionary representation of the stanza, c
        return {
            "verses": [v.to_dict() for v in self.verses]
        }


class Verse:
    words = None
    def __init__(self, text: str=None):
        self.words = text or ""

    @property
    def text(self):
        return self.words

    def to_dict(self):
        return {
            "text":self.words
        }