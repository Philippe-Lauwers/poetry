/** Wrapper class for the poem level
 * constructor
 * @param selector (id of the DOM-element)
 * @param events
 * @param buttons
 */
//
import {BaseNode} from "../API.js";

export class Suggestion extends BaseNode {

    constructor({selector="",suggestion = "", events = {}, buttons = {}} = {}) {
        super({selector, tag: "label", id:selector, events, className: "suggestion"});
        // Now `this.el` is set and registered.
        this.el.innerHTML = suggestion.text;
    }

}
