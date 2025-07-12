import {Suggestionbox} from "./suggestionboxAPI/1_SuggestionBox.js";

/**
 *Create a single shared instance of the sandbox */
let sandbox = null;

/**
 * Read-only accessor for any code that merely needs to *use*
 * the existing poem.  Will be `null` until initSandbox() runs.
 */
export const getSuggestionbox = () => Suggestionbox.instance;

export function suggestionlabelDblClick(e,target) {
    // Accept the suggestion on double-click
    document.getElementById("btn_acceptSuggestion"+target.id).click();
}

export function deactivateSuggestionbox(btnId) {
    let SB = getSuggestionbox();
    SB.deactivate();
    const btnId_parts = btnId.split("_");
    const suggId = btnId_parts.pop()
    // Mimic "disabled=true" behaviour for the label in front of the button
    document.getElementById(suggId).classList.add("selected");

    const fields = document.querySelectorAll('input[id^="struct-"]');
    let vwId
    fields.forEach(structFld => {
        if (structFld.value.includes("suggestionbox")) {
            let previous = structFld.value.split(",")[0];
            structFld.value.split(",").forEach(DOMelem => {
                if (DOMelem.includes("suggestionbox")) {
                    vwId = previous;
                }
                previous = DOMelem;
            });
        }
    });
    document.getElementById(vwId.replace("vw","v")).value = document.getElementById(suggId).innerHTML;

    //document.getElementById(btnId_parts[btnId_parts.length-2]).value = document.getElementById(btnId_parts.pop()).innerHTML;
}

export function closeSuggestionBox({e = null, target = null, YesOrNo = null, verse_id = null} = {}) {
    if (YesOrNo === false) {
        return false; // Indicates something went wrong when saving the acceptance of the suggestion
    }

    const verseId = target?.id.startsWith("btn-close-box-sug-")
        ? target.id.replace("btn-close-box-sug-", "")
        : `v-${verse_id}`;

    let SB = getSuggestionbox();
    if (SB) {
        SB.remove();
        Suggestionbox.instance = null;
    }
    let vs = document.getElementById(verseId)
    vs.readOnly = false;
    vs.classList.remove("verseEmpty");
    vs.focus();
}