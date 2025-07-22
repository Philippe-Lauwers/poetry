import {BaseNode} from "../API.js";
import {Keyword} from "./5_1_Keyword.js";

export class KeywordWrapper extends BaseNode {

    constructor({selector = "", value="", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({
            selector: selector, tag: "div", id:id, className:"keyword-wrapper", events, buttons
        });
        // Now `this.el` is set and registered
        KeywordWrapper.instance = this;
        this._btn = this.el.firstChild
        this.addKeyword({selector: this.id.replace("kww-", "kw-")+"-tmp", id:this.id.replace("kww-","kw-")+"-tmp", value:value});
    }

    addKeyword({selector = "", id = "", value = "", events = {}, buttons = {}} = {}) {
        const KW = new Keyword({selector: selector, id: id, value:value, events: events})
        if (this._btn) {
            return this.insertBefore(KW, this._btn);
        } else {
            return this.append(KW);
        }
    }
}