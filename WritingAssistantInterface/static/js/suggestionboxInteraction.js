import {Suggestionbox} from "./suggestionboxAPI/1_SuggestionBox.js";
import {enableSandbox} from "./sandboxInteraction.js";
import {receiveKeywords} from "./keywordboxInteraction.js";

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
    const theChosenOne = target.id.split("_")[target.id.split("_").length-1]
    document.querySelector(`[id^="btn_acceptSuggestion"][value="${theChosenOne}"]`).click();
}

export function deactivateSuggestionbox(btnId) {
    let SB = getSuggestionbox();
    SB.deactivate();
    const btnId_parts = btnId.split("_");
    const suggId = btnId_parts.pop()
    const verseId = btnId_parts.pop()
    // Mimic "disabled=true" behaviour for the label in front of the button
    const selectedLabel = document.getElementById("sugg_"+verseId+"_"+suggId)
        if (selectedLabel) {selectedLabel.classList.add("selected")};
        // (If we pressed the refresh button, there is no selected label)

    const fields = document.querySelectorAll('input[id^="struct-"]');
    let vwId
    fields.forEach(structFld => {
        if (structFld.value.includes("suggB")) {
            let previous = structFld.value.split(",")[0];
            structFld.value.split(",").forEach(DOMelem => {
                if (DOMelem.startsWith("suggB")) {
                    vwId = previous;
                }
                previous = DOMelem;
            });
        }
    });
}

export function activateSuggestionbox() {
    let SB = getSuggestionbox();
    SB.activate();
    // 'selected' mimics "disabled=true" behaviour for the label in front of the button -> remove class
    document
      .querySelectorAll('label[id^="sugg-"]')
      .forEach(label => label.classList.remove('my-class'));
    }

export function closeSuggestionBox({e = null, target = null, verse = null, keywords = {}} = {}) {
    if (!verse && !keywords) {
        enableSandbox();
        return false; // Indicates something went wrong when saving the acceptance of the suggestion
    }

   let SB = getSuggestionbox();
    if (SB) {
        SB.remove();
        Suggestionbox.instance = null;
    }

    if (verse || target) {
        const verseId = target?.id.startsWith("btn-close-box-sug-")
            ? target.id.replace("btn-close-box-sug-", "")
            : `v-${verse.suggAccept.verse_id}`;
        let vs = document.getElementById(verseId)
        vs.readOnly = false;
        vs.classList.remove("verseEmpty");
        vs.value = verse?.suggAccept.verse_text??"";
        enableSandbox();
        vs.focus();

        for (let struct of document.querySelectorAll('input[id^="struct-"]')) {
            if (struct.value.includes("suggB")) {
                const toCleanup = struct.value;
                const cleanedup = toCleanup.split(",").filter(item => !item.includes("suggB")).join(",");
                struct.value = cleanedup;
                if (struct.value === "") {
                    struct.value = "none";
                }
            }
        }
    };
    enableSandbox();
    if (Object.keys(keywords).length > 0) receiveKeywords(keywords);
}