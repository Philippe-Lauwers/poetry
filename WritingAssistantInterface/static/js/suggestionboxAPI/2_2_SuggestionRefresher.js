/** Wrapper class for the poem level
 * constructor
 * @param selector (id of the DOM-element)
 * @param events
 * @param buttons
 */
// poem.js
import {BaseNode} from "../API.js";

export class Suggestionrefresher extends BaseNode {

    constructor({selector = "#suggestionRefresher", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({selector, tag: "div", id, events, buttons});
        // Now `this.el` is set and registered.
    }
}
