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

@main_bp.route('/generate', methods=['POST'])
def generate():
    # proxy form data to your backend /write
    params = request.json
    resp = requests.get(f"{BACKEND_URL}/write", params=params)
    return jsonify(resp.json())

@main_bp.route('/rhymeScheme', methods=['GET'])
def rhymeScheme():
    lang = request.args.get('lang', default='1', type=str)
    form = request.args.get('form', default='1', type=str)
    params = {'lang':lang,'form':form}
    resp = requests.get(f"{BACKEND_URL}/rhymeScheme", params=params)
    print(resp.json())
    return jsonify(resp.json())

@main_bp.route('/log', methods=['POST'])
def log():
    data = request.json
    # for now just print to console
    print("FORM SUBMITTED:", data)
    return '', 204
