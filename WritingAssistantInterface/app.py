from flask import Flask, render_template, request, jsonify
import requests
import os
# for database connetivity
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

BASE = os.path.dirname(os.path.abspath(__file__))

app = Flask(
  __name__,
  static_folder=os.path.join(BASE, 'static'),
  template_folder=os.path.join(BASE, 'templates'),
)

BACKEND_URL = 'http://localhost:5050'

## Handle to database
load_dotenv(os.path.join(BASE,'..','.env'))  # reads .env and populates os.environ
print("Using DATABASE_URL:", os.getenv('DATABASE_URL'))
# This line tells SQLAlchemy where to find your database:
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # proxy form data to your backend /write
    params = request.json
    resp = requests.get(f"{BACKEND_URL}/write", params=params)
    return jsonify(resp.json())

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    # for now just print to console
    print("FORM SUBMITTED:", data)
    return '', 204

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)
