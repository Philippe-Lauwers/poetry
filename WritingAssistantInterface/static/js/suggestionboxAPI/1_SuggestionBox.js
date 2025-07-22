/** Wrapper class for the suggestion-box level
 * constructor
 * @param selector (id of the DOM-element)
 * @param events
 * @param buttons
 */
// poem.js
import {BaseNode} from "../API.js";
import {Suggestionlist} from "./2_1_SuggestionList.js";
import {Suggestionrefresher} from "./2_2_SuggestionRefresher.js";
import {closeSuggestionBox} from "../suggestionboxInteraction.js";

export class Suggestionbox extends BaseNode {

    constructor({selector = "#suggestionbox", verse = null, location=null, refresher_value = 1, suggestions = null, events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "suggB-" + verse.id

        super({selector, tag: "div", id, events, buttons});
        // Now `this.el` is set and registered.
        Suggestionbox.instance = this;

        this.addSuggestionlist({selector:selector.replace("suggB","suggL"), suggestions: suggestions})
        this.addSuggestionrefresher({verse_id: selector.replace("suggB-",""), verse:verse, refresher_value:refresher_value});
        location.append(this);
    }

    /** Adds the box that will contain the list of suggestions */
    addSuggestionlist({selector, suggestions= suggestions, events = {}, buttons = {}} = {}) {
        const sl = new Suggestionlist({selector, suggestions:suggestions})
        return this.append(sl);
    }

    /** Adds the box that will contain the refresh button */
    addSuggestionrefresher({verse_id="",verse = None, refresher_value = 1, events = {}, buttons = {}} = {}) {
        const sr = new Suggestionrefresher({
            verse: verse,
            buttons: {
                btn_close_box: {
                    id: "btn-close-box-sug-" + verse_id,
                    type: "button",
                    className: "btn",
                    alt: "Close",
                    onClick: e => {closeSuggestionBox(e, e.target);}
                },
                btn_f5_lst_sug: {
                    id: "btn-f5-lst-sug-" + verse_id,
                    value: refresher_value,
                    type: "submit",
                    formaction: "/generateVerse",
                    formmethod: "post",
                    className: "btn",
                    alt: "Generate new suggestions"
                }
            }
        });
        return this.append(sr);
    }
}
