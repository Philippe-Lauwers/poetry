import {BaseNode} from "../API.js";
import {KeywordHeader} from "./2_1_KeywordHeader.js";
import {KeywordList} from "./3_1_KeywordList.js";

export class Keywordbox extends BaseNode {

    static get n() {
    return 4;
  }

    constructor({selector = "#keywordbox", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({selector, tag: "div", id:id, events, buttons});
        // Now `this.el` is set and registered.
        Keywordbox.instance = this;
        this.addKeywordHeader({
            selector: "#keywordHeader", n: 0, buttons: {
                btn_randomKeywords: {
                    id: "btn_randomKeywords",
                    value: Keywordbox.n,
                    type: "submit",
                    formaction: "/randomKeyword",
                    formmethod: "post",
                    className: "btn",
                    alt: "Load " + String(Keywordbox.n) + " keywords"
                },
                btn_saveKeywords: {
                    id: "btn_saveKeywords",
                    type: "submit",
                    formaction: "/saveKeyword",
                    formmethod: "post",
                    className: "btn",
                    alt: "Save your keywords",
                    disabled:true
                }
            }

        });
        this.addKeywordList({selector: "#keywordList"})

        document.getElementById("btn_saveKeywords").style.display = "none";
    }

    addKeywordHeader({selector= null, events = {}, buttons = {}} = {}) {
        const KH = new KeywordHeader({
            selector, buttons
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

    get n() {
        return Keywordbox.n
    }
}
