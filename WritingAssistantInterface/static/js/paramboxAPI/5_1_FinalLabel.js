import {BaseNode} from "../API.js";

export class FinalLabel extends BaseNode {

    constructor({selector = null, id = "", value = "", htmlFor, labelText = "", events = {}, buttons = {}} = {}) {
        super({
            selector, id, tag: "label", htmlFor:htmlFor, txt: labelText, events, buttons
        }); // Now `this.el` is set and registered.
    }
}
