import {Keywordbox} from "./keywordboxAPI/1_Keywordbox.js";
import {Suggestionbox} from "./suggestionboxAPI/1_SuggestionBox.js";
import {Keyword} from "./keywordboxAPI/5_1_Keyword.js";
import {activateSuggestionbox} from "./suggestionboxInteraction.js";

/**
 * Read-only accessor for any code that merely needs to *use*
 * the existing poem.  Will be `null` until initSandbox() runs.
 */
export const getKeywordbox = () => Keywordbox.instance;

export function deactivateKeywordbox () {
    const keywordbox = getKeywordbox();
    keywordbox.header.disable();
    keywordbox.list.disable();
}

export function receiveKeywords(keywords)  {
    const keywordBox = getKeywordbox();

    if (!document.getElementById("poem_id")) {
        const idFld = document.createElement("input");
        idFld.id = idFld.name = "poem_id"
        idFld.type="hidden"
        idFld.value = keywords.id
        document.getElementsByClassName("top-pane")[0].append(idFld)
    }

    const target = firstEmptyKeyword();
    let id = target.el.id = "kw-"+keywords.keywords[0].keyword.id;
    target.el.setAttribute("name", target.el.id);

    const SB = new Suggestionbox({
                        selector: Keyword.formatID({id: parseInt(id.split("-")[1]), prefix: "suggB-kw-"}),
                        id: Keyword.formatID({id: parseInt(id.split("-")[1]), prefix: "suggB-kw-"}),
                        refresher_value: keywordBox.n,
                        verse: Keyword,
                        location: keywordBox.list,
                        suggestions: keywords.keywordSuggestions.suggestions
                    });
    activateSuggestionbox();
}

export function firstEmptyKeyword () {
    const keywordList = getKeywordbox().list;
    for (let kww of keywordList.children) {
        let kw = kww.firstChild;
        if (kw.value === "") {
            return kw;
        }
    }
}