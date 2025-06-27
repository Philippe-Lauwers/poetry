from flask import Blueprint, request, jsonify, render_template
from .poembase_from_cache import get_poem
from .poembase_config import PoembaseConfig
from .poem_repository import PoemRepository

main_bp = Blueprint('main', __name__)

@main_bp.route('/webLists', methods=['GET'])
def parameterLists():
    return jsonify({"weblists":PoembaseConfig.webLists()})


@main_bp.route('/write', methods=['GET', 'POST'])
def write_poem():
    # This endpoint writes a poem
    # - retrieving the parameters
    lang = request.args.get('lang', default='1', type=str)
    form = request.args.get('form', default='sonnet', type=str)
    nmfDim = request.args.get('nmfDim', default='random', type=str)
    try:
        nmfDim = int(nmfDim)
    except ValueError:
        pass
    print(f"Writing poem in {lang} with form {form} and nmfDim {nmfDim}")
    # - create the poem object (or get it from cache)
    poem = get_poem(lang=lang)
    poem.write(form=form, nmfDim=nmfDim)
    PoemRepository.save(poem.container)
    return jsonify({'poem': poem.container.to_dict()})


@main_bp.route('/test')
def index():
    return render_template('testBackend.html')
