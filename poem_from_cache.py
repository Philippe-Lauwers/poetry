from poembase import PoemBase

#Mapping of language codes to configuration files
LANGUAGE_CONFIG = {
    'EN': 'config/sylvia.json',
    'FR': 'config/charles.json',
    'NL': 'config/xavier.json',
}

# Dictionary that contains one Poem object per language
_poem_cache = {}

_poem_instance = None
def get_poem(lang: str='EN'):
    config_path = LANGUAGE_CONFIG.get(lang, LANGUAGE_CONFIG['EN'])

    #returns a Poem object, creating one if necessary
    # one Poem object per language, stored in a dictionary with lang(uage) as key
    if lang not in _poem_cache:
        _poem_cache[lang] = PoemBase(config=config_path)

    return _poem_cache[lang]