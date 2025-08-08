from flask import Blueprint, request, jsonify, render_template

from .keywordbase import KeywordBase
from .poem_container import Poem
from .poem_repository import PoemRepository, SuggestionRepository, KeywordSuggestionRepository, KeywordRepository
from .poem_rouge import PoemRougeScorer
from .poembase_config import PoembaseConfig
from .poembase_from_cache import get_poem

main_bp = Blueprint("main", __name__)


@main_bp.route("/webLists", methods=["GET"])
def parameterLists():
    return jsonify({"weblists": PoembaseConfig.webLists()})


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
    user_id = data.get('user_id', None)
    poem_id = data.get("poem_id", None)
    if poem_id == "undefined":
        poem_id = None
    pform = data.get("form", "1")
    nmfDim = convInt(data.get("nmfDim", "random"))
    title = data.get("poemTitle")
    keywords = {k: v for (k, v) in data.items() if k.startswith("kw-")}
    # - create the poem object (or get it from cache)
    poem = get_poem(lang=lang)
    poem.receiveUserInput(id=poem_id, form=pform, title=title, nmfDim=nmfDim, userId=user_id, userInput=keywords)
    poem.write(id=poem_id, form=pform, nmfDim=nmfDim, title=title, keywords=keywords)
    PoemRepository.save(poem.container)
    return jsonify({"poem": poem.container.to_dict()})


@main_bp.route("/generateVerse", methods=["GET", "POST"])
def write_verse():
    # This endpoint generates suggestions for a verse
    # - retrieving the parameters
    data = request.get_json(force=True) or {}

    # extract your fields (with fallbacks)
    lang = data.get("lang", "1")
    pform = data.get("form", "1")
    user_id = data.get('user_id', None)
    poem_id = data.get("poem_id", None)
    title = data.get("poemTitle", "")
    nmfDim = convInt(data.get("nmfDim", "random"))
    verses = {k: v for (k, v) in data.items() if k.startswith("v-")}
    keywords = {k: v for (k, v) in data.items() if k.startswith("kw-")}
    structure = {k: v for (k, v) in data.items() if k.startswith("struct")}

    poem = get_poem(lang=lang)
    poem.receiveUserInput(id=poem_id, form=pform, title=title, nmfDim=nmfDim, userId = user_id, structure=structure,
                          userInput=verses | keywords)
    poem.write(form=pform, nmfDim=nmfDim, structure=structure, userInput=verses, keywords=keywords)
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
    user_id = data.get('user_id', None)
    title = data.get("poemTitle")
    if title == "": title = None
    status = data.get("chckBx_final")
    if status is None: status = 1  # set to "draft"
    nmfDim = convInt(data.get("nmfDim", "random"))
    verses = {k: v for k, v in data.items() if k.startswith("v-")}
    keywords = {k: v for k, v in data.items() if k.startswith("kw-")}
    userInput = {**verses, **keywords}
    structure = {k: v for (k, v) in data.items() if k.startswith("struct")}

    poem_container = Poem(id=poem_id, lang=lang, form=pform, nmfDim=nmfDim, title=title, status=status, userId =user_id)
    poem_container.receiveUserInput(title=title, structure=structure, userInput=userInput)
    PoemRepository.save(poem_container)
    if int(status) == 2: PoemRougeScorer(poem_container).analyze()
    return jsonify({"poem": poem_container.to_dict()})


@main_bp.route("/listPoems", methods=["GET"])
def listPoems():
    user_id = request.args.get("user_id", default=None, type=str)
    poemList = PoemRepository.list(user_id=user_id)
    return jsonify({"poems": poemList})


@main_bp.route("/deletePoem", methods=["GET"])
def deletePoem():
    key = request.args.get("key", default=None, type=str)
    deleted = PoemRepository.delete(key)
    return jsonify({"deleted": deleted})


@main_bp.route("/fetchPoemByKey", methods=["GET"])
def fetchPoemByKey():
    key = request.args.get("key", default=None, type=str)
    poem = PoemRepository.fetch(key=key)
    if poem is None:
        return jsonify({"poem": None})
    return jsonify({"poem": poem.to_dict()})


@main_bp.route("/randomKeywords", methods=["GET", "POST"])
def randomKeywords():
    # This endpoint requests random keywords
    # - retrieving the parameters
    data = request.get_json(force=True) or {}
    # extract your fields (with fallbacks)
    data = request.get_json(force=True) or {}
    lang = int(data.get("lang", "1"))
    form = int(data.get("form", "1"))
    user_id = data.get('user_id', None)
    nmfDim = convInt(data.get("nmfDim", "random"))
    title = data.get("poemTitle", "")
    poem_id = data.get("poem_id", None)
    keywordList = {k: v for (k, v) in data.items() if k.startswith("kw-")}
    verseList = {k: v for (k, v) in data.items() if k.startswith("v-")}
    structure = {k: v for (k, v) in data.items() if k.startswith("struct")}

    if "btn_random1Keyword" in data.keys():
        btn = "btn_random1Keyword"
        n = 1
        # keywordList = None
    elif "btn_randomKeywords" in data.keys():
        btn = "btn_randomKeywords"
        n = int(data.get("btn_randomKeywords", "1"))
    else:
        refresher = [key for key in data if key.startswith("btn-f5-")][0]
        if refresher:
            btn = refresher
            n = int(data.get(btn)[-1])
            # keywordList = data.get("keywords", [])

    if btn == "btn_random1Keyword" or (btn.startswith("btn-f5-lst-1sug") and n == 1):
        keywordBase = KeywordBase(lang=lang, form=form, nmfDim=nmfDim, title=title, poemId=poem_id, userId=user_id)
        myKeywords = keywordBase.fetch(n=n, inputKeywords=keywordList, userInput=verseList, structure=structure)
        output = jsonify({"keywordSuggestions": True, "keywords": myKeywords})
    elif btn == "btn_randomKeywords" or (btn.startswith("btn-f5-lst-sug") and n > 1):
        keywordBase = KeywordBase(lang=lang, form=form, title=title, poemId=poem_id, userId=user_id, nmfDim=nmfDim)
        myKeywords = keywordBase.fetch(n=n, inputKeywords=keywordList, userInput=verseList, structure=structure)
        output = jsonify({"keywordSuggestions": True, "keywords": myKeywords})
    return output


@main_bp.route("/acceptKeywordSuggestion", methods=["GET", "POST"])
def accKwSuggestion():
    data = request.get_json(force=True) or {}
    suggestionCollection_id = data.get("btn_acceptSuggestion", "1").split("-")[-1]
    feedback = KeywordSuggestionRepository.accepKWCollection(suggestionCollection_id)
    return jsonify({"kwAccept": feedback})


@main_bp.route("/saveKeywords", methods=["GET", "POST"])
def saveKeywords():
    data = request.get_json(force=True) or {}
    lang = int(data.get("lang", "1"))
    form = int(data.get("form", "1"))
    user_id = data.get('user_id', None)
    nmfDim = convInt(data.get("nmfDim", "random"))
    title = data.get("poemTitle", "")
    poem_id = data.get("poem_id", None)
    keywordList = {k: v for (k, v) in data.items() if k.startswith("kw-")}
    verseList = {k: v for (k, v) in data.items() if k.startswith("v-")}
    structure = {k: v for (k, v) in data.items() if k.startswith("struct")}

    kwBase = KeywordBase(lang=lang, form=form, nmfDim=nmfDim, title=title,
                         poemId=poem_id, userId=user_id,)
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
