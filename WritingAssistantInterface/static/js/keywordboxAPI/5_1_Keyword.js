import {BaseNode} from "../API.js";

export class Keyword extends BaseNode {

    constructor({selector = "", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";
        super({
            selector: selector, tag: "input", id:id, className:"keyword", events, buttons
        });
        // Now `this.el` is set and registered
        Keyword.instance = this;
    }


}