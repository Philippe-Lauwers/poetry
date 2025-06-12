from flask import Flask, request, jsonify, render_template
from torch.distributed import rendezvous

from poem_from_cache import get_poem

app = Flask(__name__)


@app.route('/write', methods=['GET','POST'])
def write_poem():
    # This endpoint writes a poem
    # - retrieving the parameters
    lang = request.args.get('lang', default='EN', type=str)
    form = request.args.get('form', default='sonnet', type=str)
    nmfDim = request.args.get('nmfDim', default='random', type=str)
    try:
        nmfDim = int(nmfDim)
    except ValueError:
        pass

    print(f"Writing poem in {lang} with form {form} and nmfDim {nmfDim}")

    # - create the poem object (or get it from cache)
    poem = get_poem(lang=lang)
    text = poem.write(form=form,nmfDim=nmfDim)
    return jsonify({'poem': text})

@app.route('/test')
def index():
    return render_template('testBackend.html')

if __name__ == '__main__':
#    app.run(debug=False)
    app.run(debug=True, use_reloader=True)