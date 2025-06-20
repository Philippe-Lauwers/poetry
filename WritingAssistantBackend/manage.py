# manage.py

import os
from dotenv import load_dotenv
from WritingAssistantBackend.app import create_app
from WritingAssistantBackend.extensions import db
from flask_migrate import Migrate

# 1) Load your backend’s .env (adjust path if your .env lives elsewhere)
load_dotenv(os.path.join(os.path.dirname(__file__), "WritingAssistantBackend", ".env"))

# 2) Create the app via your factory
app = create_app()

# 3) Initialize migrations
migrate = Migrate(app, db)

# 4) If run directly, start on BACKEND_HOST/BACKEND_PORT (defaults to 127.0.0.1:5050)
if __name__ == "__main__":
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 5050))
    debug = app.config.get("DEBUG", False)
    app.run(host=host, port=port, debug=debug)
