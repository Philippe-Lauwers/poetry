/** Wrapper class for the suggestion list
 * constructor
 * @param selector (id of the DOM-element)
 * @param events
 * @param buttons
 */
// poem.js
import {BaseNode} from "../API.js";
import {SuggestionWrapper} from "./3_1_SuggestionWrapper.js";

// import {Wrapper} from "./3_2_Suggestion.js";

export class Suggestionlist extends BaseNode {

    constructor({selector = "#suggestionlist", verse = null, suggestions=null, events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({selector, tag: "div", id, events, buttons});
        // Now `this.el` is set and registered.
        this.addSuggestions({verse: verse, suggestions: suggestions})
    }

addSuggestions({verse = null, suggestions = [], events = {}, buttons = {}} = {}) {
    // Create a wrapper for each suggestion
    suggestions.forEach(suggestion => {
        let firstWrppr = this.firstChild;
        const suggestionWrapper = new SuggestionWrapper({
            suggestion: suggestion.suggestion,
            buttons: {
                btn_acc_sug: {
                    id: "btn_acceptSuggestion_"+verse.id+"_sugg-"+ suggestion.suggestion.id,
                    name: "btn_acceptSuggestion",
                    value:"sugg-"+ suggestion.suggestion.id,
                    type: "submit",
                    className: "btn",
                    alt: "Use this suggestion (click button or double-click label to accept)",
                }
            }
        });
        if (firstWrppr) {
            this.insertBefore(suggestionWrapper, firstWrppr);
            if (this.children.length > 6) {
                this.children[this.children.length - 1].remove();
            }
        } else {
            this.append(suggestionWrapper);
        }
    });
}


}
