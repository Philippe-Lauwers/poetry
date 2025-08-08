import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager

from .auth.routes import auth_bp
from .dbModel import User
# For database connectivity
# from flask import Flask (see above, just to remind it is needed for the app in general
# circular import with dbModel.py -> use .extensions instead
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from .extensions import db, migrate
from .routes import main_bp

# Read .env
load_dotenv()  # reads .env and populates os.environ


# creates a handle to the app with the values in .env unless otherwise specified
def create_app(config_object=None):
    app = Flask(__name__)

    db_file = os.path.join(app.root_path, os.getenv('DATABASE_FILENAME', 'poetry.db')).replace('\\', '/')

    app.config.from_object(config_object)
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'you-will-want-to-change-this'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_file}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes'),
        # …any other env-driven settings…
    )

     # 2) Enable CORS
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:5000"]}},
        supports_credentials=True
    )

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    # Set the login view here, after init_app
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 3) Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    # <-- Set the login view here, after init_app
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 4) Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # 5) Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
