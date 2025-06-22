from .poembase import PoemBase

#Mapping of language codes to configuration files
LANGUAGE_CONFIG = {
    1: 'config/sylvia.json',
    2: 'config/charles.json',
    3: 'config/xavier.json',
}

# Dictionary that contains one Poem object per language
_poem_cache = {}

_poem_instance = None
def get_poem(lang: int=1):
    config_path = LANGUAGE_CONFIG.get(lang, LANGUAGE_CONFIG[1])

    #returns a Poem object, creating one if necessary
    # one Poem object per language, stored in a dictionary with lang(uage) as key
    if lang not in _poem_cache:
        _poem_cache[lang] = PoemBase(config=config_path)

    return _poem_cache[lang]