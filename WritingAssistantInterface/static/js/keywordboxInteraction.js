import {Suggestionbox} from "./suggestionboxAPI/1_SuggestionBox.js";
import {Keywordbox} from "./keywordboxAPI/1_Keywordbox.js";
import {KeywordWrapper} from "./keywordboxAPI/4_1_KeywordWrapper.js";
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
export function activateKeywordbox () {
    const keywordbox = getKeywordbox();
    keywordbox.header.enable();
    keywordbox.list.enable();
}

export function receiveKeywords(input)  {
    const keywordBox = getKeywordbox();
    const keywordList = keywordBox.list;

    if (input.keywords) {
        if (!document.getElementById("poem_id")) {
            const idFld = document.createElement("input");
            idFld.id = idFld.name = "poem_id"
            idFld.type = "text"
            idFld.value = input.id
            document.getElementsByClassName("top-pane")[0].append(idFld)
        }

        const target = firstEmptyKeyword();
        let id = target.el.id = "kw-" + input.keywords[0].keyword.id;
        target.el.setAttribute("name", target.el.id);
        // Change button values
        let btn = target.el.nextSibling
        while (btn) {
            if (btn.tagName === "BUTTON") {
                btn.value = id;
            }
            btn = btn.nextSibling;
        }
        target.el.parentNode.id = id.replace("kw-", "kww-");

        const SB = new Suggestionbox({
            selector: Keyword.formatID({id: parseInt(id.split("-")[1]), prefix: "suggB-kw-"}),
            id: Keyword.formatID({id: parseInt(id.split("-")[1]), prefix: "suggB-kw-"}),
            refresher_value: keywordBox.n,
            verse: Keyword,
            location: keywordBox.list,
            suggestions: input.keywordSuggestions.suggestions
        });
        activateSuggestionbox();
    } else if (input.kwAccept) {
        if (input.nmfDim && input.nmfDim > 0) {
            if (document.getElementById("nmfDim").value === "random") {
                document.getElementById("nmfDim").value = input.nmfDim;
            }
        }

        let target = undefined;
        let Wr = undefined;
        let previous = 0;
        let previousWr = null;
        for (const [id, text] of Object.entries(input.kwAccept.keywords)) {
            if (target == undefined) {
                target = document.getElementById("kw-" + id);
                target.value = text;
                Wr = Keyword.getWrapper(target).parent;
            } else {
                Wr = keywordList.addKeywordWrapper({
                    selector: "kww-" + id,
                    id:"kww-"+id,
                    value:text,
                    buttons: previousWr.buttons,
                    events: previousWr.events
                });
            }
            previous = id;
            previousWr = Wr;

            for (const btn of Wr.el.children) {
                if (btn.id.startsWith("btn_del")) {
                    btn.value = "kw-"+id
                    btn.style.display = "inline-block";
                    btn.disabled = false;
                } else if (btn.id.startsWith("btn_random")) {
                    btn.value = "kw-"+id;
                    btn.style.display = "none";
                }
            }
        activateKeywordbox()
        }
    }
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