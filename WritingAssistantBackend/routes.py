from flask import Blueprint, request, jsonify, render_template

from .poembase_from_cache import get_poem
from .poembase_config import PoembaseConfig
from .poem_repository import PoemRepository

main_bp = Blueprint('main', __name__)

@main_bp.route('/webLists', methods=['GET'])
def parameterLists():
    return jsonify({'weblists':PoembaseConfig.webLists()})

@main_bp.route('/poemForm', methods=['GET'])
def poemForm():
    lang = request.args.get('lang', default='1', type=str)
    form = request.args.get('form', default='sonnet', type=str)
    return jsonify({'rhymeScheme': PoembaseConfig.Poemforms.webElements(lang=lang, form=form)})

def convInt(value):
    try:
        return int(value)
    except ValueError:
        return value
@main_bp.route('/generatePoem', methods=['GET', 'POST'])
def write_poem():
    # This endpoint writes a poem
    # - retrieving the parameters
    data = request.get_json(force=True) or {}

    # extract your fields (with fallbacks)
    lang = data.get('lang', '1')
    pform = data.get('form', '1')
    nmfDim = convInt(data.get('nmfDim', 'random'))
    print(f"Writing poem in {lang} with form {pform} and nmfDim {nmfDim}")
    # - create the poem object (or get it from cache)
    poem = get_poem(lang=lang)
    poem.write(form=pform, nmfDim=nmfDim)
    PoemRepository.save(poem.container)
    return jsonify({'poem': poem.container.to_dict()})

@main_bp.route('/generateVerse', methods=['GET','POST'])
def write_verse():
    # This endpoint generates suggestions for a verse
    # - retrieving the parameters
    data = request.get_json(force=True) or {}

    # extract your fields (with fallbacks)
    lang = data.get('lang', '1')
    pform = data.get('form', '1')
    nmfDim = convInt(data.get('nmfDim', 'random'))
    verses = {k:v for (k,v) in data.items() if k.startswith('v-')}
    structure = {k:v for (k,v) in data.items() if k.startswith('struct')}

    poem = get_poem(lang=lang)
    poem.write(form=pform, nmfDim=nmfDim, structure=structure, userInput=verses)

    pass

@main_bp.route('/test')
def index():
    return render_template('testBackend.html')
