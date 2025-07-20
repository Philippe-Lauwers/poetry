import {BaseNode} from "../API.js";
import {Keyword} from "./5_1_Keyword.js";

export class KeywordWrapper extends BaseNode {

    constructor({selector = "", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({
            selector: selector, tag: "div", id:id, className:"keyword-wrapper", events, buttons
        });
        // Now `this.el` is set and registered
        KeywordWrapper.instance = this;
        this._btn = this.el.firstChild
        this.addKeyword({selector: this.id.replace("kww-", "kw-"), name:this.id.replace("kww-","kw-")});
    }

    addKeyword({selector = "", events = {}, buttons = {}} = {}) {
        const KW = new Keyword({selector: "kw-1", buttons: buttons})
        if (this._btn) {
            return this.insertBefore(KW, this._btn);
        } else {
            return this.append(KW);
        }
    }
}