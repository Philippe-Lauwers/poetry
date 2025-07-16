# WritingAssistantInterface/routes.py

import os
import requests
import random
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

    return render_template('index.html', weblists=weblists, weblists_form=weblists_form,
                           randomPlaceholder=pickPlaceholder())

def pickPlaceholder():
    placeholders = [
          # Shakespearean */
          "Pray, endow upon this tome thine own beauteous epithet.",
          "Anoint this scroll with thy most wondrous moniker.",
          "Do grant this work the charm of thy fairest title.",
          "Bestow, I beseech thee, upon these words thy peerless name.",
          # Poe‑flavored */
          "Whisper here the name that haunts thy darkling soul.",
          "Imprint upon this page the shadowed name thou hold’st dearest.",
          "Reveal the title that stirs within thy midnight heart.",
          "Inscribe here the epithet that lingers in thy sombre reveries.",
          # Wilde‑esque */
          "Dare to christen this modest volume with your most exquisite epithet.",
          "Impart upon these pages the graceful title of thine own inventing.",
          "Endow this little masterpiece with the flourish of your finest name.",
          "Bestow a moniker upon this work that even my wit might envy.",
          "Grant this humble opus the elegance of your singular designation.",
          "Crown this collection with whatever title your genius deems worthy."
        ]
    return random.choice(placeholders)


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

@main_bp.route('/acceptSuggestion', methods=['POST'])
def accSuggestion():
    params = request.get_json(force=True)
    # print(request.form.get('action'))
    resp = requests.post(f"{BACKEND_URL}/acceptSuggestion",
                         json=params,  # <— send JSON, not form-data
                            headers={'Content-Type': 'application/json'})
    return jsonify(resp.json())

@main_bp.route('/poemForm', methods=['GET'])
def poemForm():
    lang = request.args.get('lang', default='1', type=str)
    form = request.args.get('form', default='1', type=str)
    params = {'lang':lang,'form':form}
    resp = requests.get(f"{BACKEND_URL}/poemForm", params=params)
    return jsonify(resp.json())

@main_bp.route('/savePoem', methods=['POST'])
def savePoem():
    print("Saving poem...")
    # proxy form data to your backend /write
    params = request.get_json(force=True)
    resp = requests.post(f"{BACKEND_URL}/savePoem",
        json=params,               # <— send JSON, not form-data
        headers={'Content-Type': 'application/json'})
    return jsonify(resp.json())

@main_bp.route('/log', methods=['POST'])
def log():
    data = request.json
    # for now just print to console
    print("FORM SUBMITTED:", data)
    return '', 204
