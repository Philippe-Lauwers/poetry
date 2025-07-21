import {BaseNode} from "../API.js";
import {KeywordWrapper} from "../keywordboxAPI/4_1_KeywordWrapper.js";

export class KeywordList extends BaseNode {

    constructor({selector = "", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({
            selector, id, tag: "div", events, buttons
        });
        // Now `this.el` is set and registered.
        KeywordList.instance = this;

        this.addKeywordWrapper({
            selector: "kww-1-tmp",
            id: "kww-1-tmp",
            buttons: {
                btn_random1Keyword: {
                    id: "btn_random1Keyword",
                    value: "kw-1",
                    type: "submit",
                    formaction: "/generateKeyword",
                    formmethod: "post",
                    className: "btn",
                    title: "Request a new keyword" // "alt" is for <img>, not buttons
                }
            }
        });
    }

    addKeywordWrapper({id = "", buttons:buttons} = {}) {
        const KWW = new KeywordWrapper({selector:"kww-1", buttons:buttons})
        return this.insertBefore(KWW, this._btn);
    }

    disable() {
        for (let kww of this.children) {
            for (let kww_child of kww.children) {
                if (kww_child.id.startsWith("btn_random")) {
                    kww_child.el.disabled = true;
                } else if (kww_child.id.startsWith("kw-")) {
                    kww_child.el.readOnly = true;
                }
                for(let btn in kww.buttons) {
                    document.getElementById(btn).disabled = true;
                }
            }
        }
    }
}