import {BaseNode} from "../API.js";
import {KeywordHeader} from "./2_1_KeywordHeader.js";
import {KeywordList} from "./3_1_KeywordList.js";

export class Keywordbox extends BaseNode {

    constructor({selector = "#keywordbox", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({selector, tag: "div", id:id, events, buttons});
        // Now `this.el` is set and registered.
        Keywordbox.instance = this;

        this.addKeywordHeader({selector: "#keywordHeader",n:0});
        this.addKeywordList({selector: "#keywordList"})
    }

    addKeywordHeader({selector= null, events = {}, buttons = {}} = {}) {
        const n = 4;
        const KH = new KeywordHeader({
            selector, buttons: {
                btn_randomKeywords: {
                    id: "btn_randomKeywords",
                    value: n,
                    type: "submit",
                    formaction: "/randomKeyword",
                    formmethod: "post",
                    className: "btn",
                    alt: "Load " + String(n) + " keywords"
                }
            }
        })
        return this.append(KH);
    }

    addKeywordList({selector = null, events = {}, buttons = {}} = {}) {
        const KL = new KeywordList({selector})
        return this.append(KL);
    }

    get header() {
        for (let elem of this.children) {
            if (elem.id == "keywordHeader") return elem;
        }
    }

    get list() {
        for (let elem of this.children) {
            if (elem.id == "keywordList") return elem;
        }
    }
}
