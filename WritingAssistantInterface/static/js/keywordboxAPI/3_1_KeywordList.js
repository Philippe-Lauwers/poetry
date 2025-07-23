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
            buttons: {
                btn_random1Keyword: {
                    id: "btn_random1Keyword",
                    value: "kw-1",
                    type: "submit",
                    formaction: "/generateKeyword",
                    formmethod: "post",
                    className: "btn",
                    alt: "Request a new keyword" // "alt" is for <img>, not buttons
                },
                btn_deleteKeyword: {
                    id: "btn_deleteKeyword",
                    value: "kw-1",
                    type: "submit",
                    formaction: "/deleteKeyword",
                    formmethod: "post",
                    className: "btn",
                    disabled: true,
                    alt: "Delete keyword" // "alt" is for <img>, not buttons
                }
            }
        });
        for (let el of wrapper.el.querySelectorAll("button")) {
            if (el.id.startsWith("btn_del")) {
                el.style.display = "none";
            }
            el.value = wrapper.firstChild.name;
        }
    }

    addKeywordWrapper({id = "", value="", buttons:buttons} = {}) {
        const KWW = new KeywordWrapper({selector:id, value:value, buttons:buttons})
        return this.append(KWW);
    }

    disable() {
        for (let kww of this.children) {
            for (let kww_child of kww.children) {
                if (kww_child.id.startsWith("kw-")) {
                    kww_child.el.readOnly = true;
                }
                const buttonColl = document.querySelectorAll("#btn_deleteKeyword, #btn_random1Keyword");
                buttonColl.forEach(button => {
                    button.disabled = true
                })
            }
        }
    }

    enable() {
        for (let kww of this.children) {
            for (let kww_child of kww.children) {
                if (kww_child.id.startsWith("kw-")) {
                    kww_child.el.readOnly = false;
                }
                const buttonColl = document.querySelectorAll("#btn_deleteKeyword, #btn_random1Keyword");
                buttonColl.forEach(button => {
                    button.disabled = false;
                })
            }
        }
    }
}