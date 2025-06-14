from flask import Flask, render_template, request, jsonify
import requests
import os

BASE = os.path.dirname(os.path.abspath(__file__))

app = Flask(
  __name__,
  static_folder=os.path.join(BASE, 'static'),
  template_folder=os.path.join(BASE, 'templates'),
)

BACKEND_URL = 'http://localhost:5050'

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
    app.run(port=5000, debug=True)
