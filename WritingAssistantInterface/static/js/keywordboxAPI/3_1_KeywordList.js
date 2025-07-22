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

        const wrapper = this.addKeywordWrapper({
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
                },
                btn_deleteKeyword: {
                    id: "btn_deleteKeyword",
                    value: "kw-1",
                    type: "submit",
                    formaction: "/deleteKeyword",
                    formmethod: "post",
                    className: "btn",
                    disabled: true,
                    title: "Delete keyword" // "alt" is for <img>, not buttons
                }
            }
        });
        for (let el of wrapper.el.children) {
            if (el.id.startsWith("btn_del")) {
                el.style.display = "none";
            }
        }
    }

    addKeywordWrapper({id = "", value="", buttons:buttons} = {}) {
        const KWW = new KeywordWrapper({selector:id!==""?id:"kww-1", value:value, buttons:buttons})
        return this.append(KWW);
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
    enable() {
        for (let kww of this.children) {
            for (let kww_child of kww.children) {
                if (kww_child.id.startsWith("btn_random")) {
                    kww_child.el.disabled = false;
                } else if (kww_child.id.startsWith("btn_del")) {
                    kww_child.el.disabled = false;
                    kww_child.el.style.display = "inline-block";
                } else if (kww_child.id.startsWith("kw-")) {
                    kww_child.el.readOnly = false;
                }
                for(let btn in kww.buttons) {
                    document.getElementById(btn).disabled = false;
                }
            }
        }
    }
}