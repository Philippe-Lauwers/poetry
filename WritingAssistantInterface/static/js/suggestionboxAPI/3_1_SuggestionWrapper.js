/** Wrapper class for the suggestion wrapper level (to place a button next to a label
 * constructor
 * @param selector (id of the DOM-element)
 * @param events
 * @param buttons
 */
import {BaseNode} from "../API.js";
import {Suggestion} from "./3_2_Suggestion.js";
import {suggestionlabelDblClick} from "../suggestionboxInteraction.js";


export class SuggestionWrapper extends BaseNode {

    constructor({suggestion = null, events = {}, buttons = {}} = {}) {
        super({tag: "div", className:"suggestionWrapper", events, buttons});
        // Now `this.el` is set and registered.
        this.addSuggestion({suggestion: suggestion});
    }

    // /** Adds the box that will contain the list of suggestions */
    addSuggestion({suggestion = null}) {
        const sl = new Suggestion({
            id: "sugg-"+ suggestion.id,
            suggestion: suggestion,
            events: {dblclick: e => suggestionlabelDblClick(e, e.target)}
        });
        for (let elem of this.el.children) {
            const elem_tag = elem.tagName.toLowerCase();
            switch (elem_tag) {
                case "button":
                    this.el.insertBefore(sl.el, elem)
                    break;
            }
        }

         return sl;
    }

}
