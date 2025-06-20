from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# for database connetivity
# from flask_sqlalchemy import SQLAlchemy

load_dotenv()

BASE = os.path.dirname(os.path.abspath(__file__))
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5050")

app = Flask(
    __name__,
    static_folder=os.path.join(BASE, 'static'),
    template_folder=os.path.join(BASE, 'templates'),
)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "abcdefghijklmnopqrstuvwxyz012345")

from routes import main_bp

app.register_blueprint(main_bp)

if __name__ == '__main__':
    # Read INTERFACE_PORT from the environment, default to 5000
    port = int(os.getenv("INTERFACE_PORT", 5000))
    # (Optionally) allow binding to another host via INTERFACE_HOST
    host = os.getenv("INTERFACE_HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=True, use_reloader=False)
