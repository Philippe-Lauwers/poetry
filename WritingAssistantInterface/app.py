from flask import Flask, send_from_directory, request, jsonify
import requests

app = Flask(__name__, template_folder='templates')

BACKEND_URL = 'http://localhost:5050'   # your LM server

@app.route('/')
def home():
    return send_from_directory('templates', 'index.html')

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
