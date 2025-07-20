import {deactivateParambox} from "./paramboxInteraction.js";
import {disableGenBtn, getSandbox, disableSandbox} from "./sandboxInteraction.js";
import {deactivateSuggestionbox} from "./suggestionboxInteraction.js";
import {deactivateKeywordbox} from "./keywordboxInteraction.js"

export class Submit {

    static handler(e) {
        if (e.submitter.id == "btn_generatePoem") {
            document.getElementById("lang").disabled = false;
            setTimeout(() => {
                deactivateParambox(e, e.submitter);
                disableGenBtn(e, {includeFld: true});
                disableSandbox();
            }, 0);
        } else if (e.submitter.id == "btn_generateVerse" || e.submitter.id.startsWith("btn-f5-lst-sug")) {
            setTimeout(() => {
                deactivateParambox(e, e.submitter);
                disableSandbox(e);
                for (let el of e.submitter.parentNode.childNodes) {
                        el.readOnly = true;
                  }
                e.submitter.disabled = true;
            }, 0);
            if (e.submitter.id.startsWith("btn-f5-lst-sug")) {
                deactivateSuggestionbox(e.submitter.id);
            }
        } else if (e.submitter.id.startsWith("btn_acceptSuggestion")) {
            deactivateSuggestionbox(e.submitter.id);
            disableSandbox()
        } else if (e.submitter.id.includes("Keyword")) {
            deactivateKeywordbox(e.submitter.id);
        }
    }
}