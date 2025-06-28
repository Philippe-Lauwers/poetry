from .poembase import PoemBase

# Dictionary that contains one Poem object per language
_poem_cache = {}

def get_poem(lang: int=1):
    #returns a Poem object, creating one if necessary
    # one Poem object per language, stored in a dictionary with lang(uage) as key
    if lang not in _poem_cache:
        _poem_cache[lang] = PoemBase(lang)
    pass
    return _poem_cache[lang]