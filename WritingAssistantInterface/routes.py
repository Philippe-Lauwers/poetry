# WritingAssistantInterface/routes.py

import os
import requests
from flask import Blueprint, render_template, request, jsonify

# Load env (optional if already done in app.py)
from dotenv import load_dotenv
load_dotenv()

# Compute backend URL once
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5050")

# Create a Blueprint
main_bp = Blueprint(
    "main",
    __name__,
    static_folder="static",
    template_folder="templates",
)

@main_bp.route('/')
def home():
    resp = requests.get(f"{BACKEND_URL}/webLists")
    weblists = resp.json()['weblists']

    # Look for the 'form' section of the json input
    weblists_form = None
    for section in weblists:
        if 'form' in section.keys(): # section will only have one key anyway
            weblists_form = section['form']
            break

    return render_template('index.html',weblists=weblists, weblists_form=weblists_form)

@main_bp.route('/generatePoem', methods=['POST'])
def genPoem():
    # proxy form data to your backend /write
    params = request.get_json(force=True)
    resp = requests.post(f"{BACKEND_URL}/generatePoem",
        json=params,               # <— send JSON, not form-data
        headers={'Content-Type': 'application/json'})
    return jsonify(resp.json())

@main_bp.route('/generateVerse', methods=['POST'])
def genVerse():
    # proxy form data to your backend /write
    params = request.get_json(force=True)
    resp = requests.post(f"{BACKEND_URL}/generateVerse",
        json=params,               # <— send JSON, not form-data
        headers={'Content-Type': 'application/json'})
    return jsonify(resp.json())

@main_bp.route('/poemForm', methods=['GET'])
def poemForm():
    lang = request.args.get('lang', default='1', type=str)
    form = request.args.get('form', default='1', type=str)
    params = {'lang':lang,'form':form}
    resp = requests.get(f"{BACKEND_URL}/poemForm", params=params)
    return jsonify(resp.json())

@main_bp.route('/log', methods=['POST'])
def log():
    data = request.json
    # for now just print to console
    print("FORM SUBMITTED:", data)
    return '', 204
