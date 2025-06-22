from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from .poembase_from_cache import get_poem
# For database connectivity
# from flask import Flask (see above, just to remind it is needed for the app in general
# circular import with dbModel.py -> use .extensions instead
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from .extensions import db, migrate

# Read .env
load_dotenv()  # reads .env and populates os.environ


# creates a handle to the app with the values in .env unless otherwise specified
def create_app(config_object=None):
    app = Flask(__name__)
    # 1) Load your config

    db_file = os.path.join(app.root_path, os.getenv('DATABASE_FILENAME', 'poetry.db')).replace('\\', '/')

    app.config.from_object(config_object)
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'you-will-want-to-change-this'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_file}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes'),
        # …any other env-driven settings…
    )

    # app.config['SQLALCHEMY_ECHO'] = True  # optionally see SQL logs
    # 2) Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # 3) load routing from routes.py
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app


from .dbModel import *
app = create_app()
