from flask import Blueprint, request, jsonify, render_template

from .keywordbase import KeywordBase
from .poembase_from_cache import get_poem
from .poembase_config import PoembaseConfig
from .poem_repository import PoemRepository, SuggestionRepository, KeywordSuggestionRepository, KeywordRepository
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
    # extract your fields (with fallbacks)
    lang = data.get("lang", "1")
    pform = data.get("form", "1")
    nmfDim = convInt(data.get("nmfDim", "random"))
    title = data.get("poemTitle")
    print(f"Writing poem in {lang} with form {pform} and nmfDim {nmfDim}")
    # - create the poem object (or get it from cache)
    poem = get_poem(lang=lang)
    poem.write(form=pform, nmfDim=nmfDim, title=title)
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
    title = data.get("poemTitle", "")
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

    feedback = SuggestionRepository.acceptSuggestion(verse_id, suggestion_id)
    return jsonify({"suggAccept": feedback})

@main_bp.route("/savePoem", methods=["GET", "POST"])
def savePoem():
    # This endpoint saves the poem to the database
    # - retrieving the parameters
    data = request.get_json(force=True) or {}
    # extract your fields (with fallbacks)
    poem_id = data.get("poem_id", None)
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

@main_bp.route("/randomKeywords", methods=["GET", "POST"])
def randomKeywords():
    # This endpoint requests random keywords
    # - retrieving the parameters
    data = request.get_json(force=True) or {}
    # extract your fields (with fallbacks)
    data = request.get_json(force=True) or {}
    lang = int(data.get("lang", "1"))
    form = int(data.get("form", "1"))
    nmfDim = convInt(data.get("nmfDim", "random"))
    title = data.get("poemTitle", "")
    poem_id = data.get("poem_id", None)
    keywordList = {k: v for (k, v) in data.items() if k.startswith("kw-")}
    if "btn_random1Keyword" in data.keys():
        btn = "btn_random1Keyword"
        keywordList = None
    elif "btn_randomKeywords" in data.keys():
        btn = "btn_randomKeywords"
        n = int(data.get("btn_randomKeywords","1"))
    else:
        refresher = [key for key in data if key.startswith("btn-f5-")][0]
        if refresher:
            btn = refresher
            n = int(data.get(btn)[-1])
            # keywordList = data.get("keywords", [])

    if btn == "btn_random1Keyword":
        return jsonify({"keywords": KeywordBase(lang=lang, form=form, nmfDim=nmfDim, title=title,
                                                poemId=poem_id).fetch(inputKeywords=keywordList)})
    elif btn == "btn_randomKeywords" or (btn.startswith("btn-f5-") and n > 1):
        return jsonify({"keywords": KeywordBase(lang=lang, form=form, title=title, poemId=poem_id).fetch(n=n,
                                                                                                          inputKeywords=keywordList)})

@main_bp.route("/acceptKeywordSuggestion", methods=["GET", "POST"])
def accKwSuggestion():
    data = request.get_json(force=True) or {}
    suggestionCollection_id = data.get("btn_acceptSuggestion", "1").split("-")[-1]
    feedback = KeywordSuggestionRepository.accepKWCollection(suggestionCollection_id)
    return jsonify ({"kwAccept": feedback})


@main_bp.route("/saveKeywords", methods=["GET", "POST"])
def saveKeywords():
    data = request.get_json(force=True) or {}
    lang = int(data.get("lang", "1"))
    form = int(data.get("form", "1"))
    nmfDim = convInt(data.get("nmfDim", "random"))
    title = data.get("poemTitle", "")
    poem_id = data.get("poem_id", None)
    keywordList = {k: v for (k, v) in data.items() if k.startswith("kw-")}
    verseList = {k: v for (k, v) in data.items() if k.startswith("v-")}
    structure = {k: v for (k, v) in data.items() if k.startswith("struct")}

    kwBase = KeywordBase(lang=lang, form=form, nmfDim=nmfDim, title=title,
                                            poemId=poem_id)
    status = kwBase.save(inputKeywords=keywordList, userInput=verseList, structure=structure)

    return jsonify({"keywordsSaved": status})


@main_bp.route("/deleteKeyword", methods=["GET", "POST"])
def deleteKeyword():
    data = request.get_json(force=True) or {}
    keyword_id = data.get("btn_deleteKeyword", "1").split("-")[-1]
    feedback = KeywordRepository.deleteKeyword(keyword_id)
    return jsonify({"kwDelete": feedback})

@main_bp.route("/test")
def index():
    return render_template("testBackend.html")
