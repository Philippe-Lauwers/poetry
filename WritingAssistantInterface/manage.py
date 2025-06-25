# WritingAssistantInterface/manage.py

import os
from dotenv import load_dotenv

# 1) Load environment variables from .flaskenv in this folder

here = os.path.dirname(__file__)
load_dotenv(os.path.join(here,'WritingAssistantInterface, '.flaskenv'))

# 2) Import your Flask app object (defined at module level in app.py)
from app import app

# 3) Run the app when invoked directly
if __name__ == "__main__":
    host = os.getenv("INTERFACE_HOST", "127.0.0.1")
    port = int(os.getenv("INTERFACE_PORT", 5000))
    debug = app.config.get("DEBUG", True)
    app.run(host=host, port=port, debug=debug)
