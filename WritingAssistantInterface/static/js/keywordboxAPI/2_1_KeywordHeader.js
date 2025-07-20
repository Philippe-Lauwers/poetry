import {BaseNode} from "../API.js";
import {KeywordLabel} from "../keywordboxAPI/2_2_KeywordLabel.js";

export class KeywordHeader extends BaseNode {

    constructor({selector = "", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({
            selector, tag: "div", id, events, buttons
        });
        // Now `this.el` is set and registered.
        KeywordHeader.instance = this;

        this._btn = this.el.firstChild
        this.addLabel()
    }

    addLabel({id = "", htmlFor = ""} = {}) {
        const L = new KeywordLabel({id: "label_" + this.id, labelText: "Keywords"})
        return this.insertBefore(L, this._btn);
    }

    disable() {
        this._btn.disabled = true;
    }

}