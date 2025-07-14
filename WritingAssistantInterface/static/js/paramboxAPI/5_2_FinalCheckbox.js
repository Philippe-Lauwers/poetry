import {BaseNode} from "../API.js";

export class FinalCheckbox extends BaseNode {

    constructor({selector = null, id = "", events = {}, buttons = {}} = {}) {
        super({
            selector, id, tag: "input", type: "checkbox", events, buttons
        }); // Now `this.el` is set and registered.
        this.el.disabled = true; // enabled when appropriate content is written
    }

}
