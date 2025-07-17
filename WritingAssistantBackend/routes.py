from flask import Blueprint, request, jsonify, render_template

from .poembase_from_cache import get_poem
from .poembase_config import PoembaseConfig
from .poem_repository import PoemRepository, SuggestionRepository
from .poem_container import Poem
from .poem_rouge import PoemRougeScorer

main_bp = Blueprint("main", __name__)

@main_bp.route("/webLists", methods=["GET"])
def parameterLists():
    return jsonify({"weblists":PoembaseConfig.webLists()})

@main_bp.route("/poemForm", methods=["GET"])
def poemForm():
    lang = request.args.get("lang", default="1", type=str)
    form = request.args.get("form", default="sonnet", type=str)
    return jsonify({"rhymeScheme": PoembaseConfig.Poemforms.webElements(lang=lang, form=form)})

def convInt(value):
    try:
        return int(value)
    except ValueError:
        return value

@main_bp.route("/generatePoem", methods=["GET", "POST"])
def write_poem():
    # This endpoint writes a poem
    # - retrieving the parameters
    data = request.get_json(force=True) or {}
    debug = False
    if (debug):
        return jsonify({
            "poem": {
                "id": 20,
                "parameters": {
                    "form": "1",
                    "nmfDim": 46
                },
                "stanzas": [
                    {
                        "stanza": {
                            "id": 38,
                            "verses": [
                                {"verse": {"id": 109, "text": "i love the old rock band live band , as well"}},
                                {"verse": {"id": 110, "text": "i love jazz music and i love young children"}},
                                {"verse": {"id": 111, "text": "i love playing pop music in the kitchen"}},
                                {"verse": {"id": 112, "text": "it 's one of my favorite songs to tell"}}
                            ]
                        }
                    },
                    {
                        "stanza": {
                            "id": 39,
                            "verses": [
                                {"verse": {"id": 113, "text": "this is my first solo album and i love him"}},
                                {"verse": {"id": 114, "text": "the lyrics of the song are numerous"}},
                                {"verse": {"id": 115, "text": "the sound of the song sounds fabulous"}},
                                {"verse": {"id": 116, "text": "i love hip hop on my big ride to the gym"}}
                            ]
                        }
                    },
                    {
                        "stanza": {
                            "id": 40,
                            "verses": [
                                {"verse": {"id": 117, "text": "i like playing rock guitar , to be honest"}},
                                {"verse": {"id": 118, "text": "i play bass guitar in a big way"}},
                                {"verse": {"id": 119, "text": "i would love to sing a solo artist"}}
                            ]
                        }
                    },
                    {
                        "stanza": {
                            "id": 41,
                            "verses": [
                                {"verse": {"id": 120, "text": "i had a lot of fun playing punk rock ballet"}},
                                {"verse": {"id": 121, "text": "i was a fan of indie rock rock rock music list"}},
                                {"verse": {"id": 122, "text": "i love singing every single day"}}
                            ]
                        }
                    }
                ]
            }
        })
    # extract your fields (with fallbacks)
    lang = data.get("lang", "1")
    pform = data.get("form", "1")
    nmfDim = convInt(data.get("nmfDim", "random"))
    print(f"Writing poem in {lang} with form {pform} and nmfDim {nmfDim}")
    # - create the poem object (or get it from cache)
    poem = get_poem(lang=lang)
    poem.write(form=pform, nmfDim=nmfDim)
    PoemRepository.save(poem.container)
    return jsonify({"poem": poem.container.to_dict()})

@main_bp.route("/generateVerse", methods=["GET","POST"])
def write_verse():
    # This endpoint generates suggestions for a verse
    # - retrieving the parameters
    data = request.get_json(force=True) or {}

    # extract your fields (with fallbacks)
    lang = data.get("lang", "1")
    pform = data.get("form", "1")
    title = data.get("title", "")
    nmfDim = convInt(data.get("nmfDim", "random"))
    verses = {k:v for (k,v) in data.items() if k.startswith("v-")}
    structure = {k:v for (k,v) in data.items() if k.startswith("struct")}

    poem = get_poem(lang=lang)
    poem.receiveUserInput(form=pform ,title=title, nmfDim=nmfDim, structure= structure, userInput=verses)
    poem.write(form=pform, nmfDim=nmfDim, structure=structure, userInput=verses)
    PoemRepository.save(poem.container)
    return jsonify({"poem": poem.container.to_dict()})

@main_bp.route("/acceptSuggestion", methods=["GET", "POST"])
def accSuggestion():
    # This endpoint writes to the database that a user decided to work with a suggestion
    # - retrieving the parameters
    data = request.get_json(force=True) or {}
    # extract your fields (with fallbacks)
    suggestion_id = data.get("btn_acceptSuggestion", "1").split("-")[-1]
    for key, value in data.items():
        if '-s-' in key:
            vwLst = value.split(',')
            prevVw = vwLst[0]
            for vw in vwLst:
                if vw.startswith("suggB"):
                    verse_id = prevVw.split("-")[-1]
                    break
                prevVw = vw

    status = SuggestionRepository.acceptSuggestion(verse_id, suggestion_id)
    return jsonify({"suggAccept": status, "verse_id": verse_id})

@main_bp.route("/savePoem", methods=["GET", "POST"])
def savePoem():
    # This endpoint saves the poem to the database
    # - retrieving the parameters
    data = request.get_json(force=True) or {}
    # extract your fields (with fallbacks)
    poem_id = data.get("poem_id", "1")
    lang = data.get("lang", "1")
    pform = data.get("form", "1")
    title = data.get("poemTitle")
    if title == "": title = None
    status = data.get("chckBx_final")
    if status is None: status = 1 # set to "draft"
    nmfDim = convInt(data.get("nmfDim", "random"))
    verses = {k: v for (k, v) in data.items() if k.startswith("v-")}
    structure = {k: v for (k, v) in data.items() if k.startswith("struct")}

    poem_container = Poem(id=poem_id, lang=lang, form=pform, nmfDim=nmfDim, title=title, status=status)
    poem_container.receiveUserInput(title = title, structure = structure, userInput = verses)
    PoemRepository.save(poem_container)
    if int(status) == 2: PoemRougeScorer(poem_container).analyze()
    return jsonify({"poem": poem_container.to_dict()})

@main_bp.route("/test")
def index():
    return render_template("testBackend.html")
