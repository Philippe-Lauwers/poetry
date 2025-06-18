from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from .poem_from_cache import get_poem
# For database connectivity
# from flask import Flask (see above, just to remind it is needed for the app in general
# circular import with dbModel.py -> use .extensions instead
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from .extensions import db, migrate


app = Flask(__name__)
# Allow requests coming from your frontend at localhost:5050
CORS(app, resources={r"/write": {"origins": "http://localhost:5000"}})  # allow client → backend

# Handle to database
load_dotenv()  # reads .env and populates os.environ
# This line tells SQLAlchemy where to find the  database:
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
print("Using DATABASE_URL:", app.config['SQLALCHEMY_DATABASE_URI'])
db.init_app(app)
# Pass app and db to Migrate
migrate.init_app(app, db)

from .dbModel import Users, PoemLanguages, RhymeSchemes, RhymeSchemeElements, Themes, ThemeDescriptors, Actions, Poems, \
    Stanzas, Verses


@app.route('/write', methods=['GET', 'POST'])
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
    text = poem.write(form=form, nmfDim=nmfDim)
    return jsonify({'poem': text})


@app.route('/test')
def index():
    return render_template('testBackend.html')


if __name__ == '__main__':
    #    app.run(debug=False)
    app.run(port=5050, debug=True, use_reloader=True)
