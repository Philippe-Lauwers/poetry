/** Wrapper class for the poem level
 * constructor
 * @param selector (id of the DOM-element)
 * @param events
 * @param buttons
 */
//
import {BaseNode} from "../API.js";

export class Suggestion extends BaseNode {

    constructor({suggestion = "", events = {}, buttons = {}} = {}) {
        super({tag: "label", id:"sugg-"+suggestion.id, events, className: "suggestion"});
        // Now `this.el` is set and registered.
        this.el.innerHTML = suggestion.text;
    }

}
