/** Add a new stanza and return the Stanza wrapper */
import {BaseNode} from "../API.js";
import {Verse} from "./4_Verse.js";

export class VerseWrapper extends BaseNode {
    static #nVerseWrapper = 0;

    constructor({selector = null, id = null, events = {}, buttons = {}} = {}) {
        const isNew = id == null;
        const serial = isNew ? ++VerseWrapper.#nVerseWrapper : id;
        const finalID = VerseWrapper.formatID({id: serial, prefix: "vw-", suffix: isNew ? "-tmp" : ""});
        super({
            id: finalID, tag: "div", className: "verse-wrapper", events, buttons
        }); // Now `this.el` is set and registered.
    }

    /** Add a new verseWrapper and return the verseWrapper wrapper */
    addVerse({selector=null,id = null, value = "", events = {}} = {}) {
        const v = new Verse({id: id, value: value, events: events})
        if (this.el.firstChild) {
            for (let b of this.el.children) {
                const b_id = b.id
                switch (b.id.substring(b_id.indexOf("-")+1,b_id.lastIndexOf("-"))) {
                    case "gen-v":
                        b.id = b.id.concat(v.id.substring(v.id.indexOf("-")+1,v.id.lastIndexOf("-")))
                }
            }
            this.el.insertBefore(v.el,this.el.firstChild)
            return v;
        } else {
            return this.append(v);
        }
    }


    /**
     * === HELPER METHODS/FUNCTIONS === */
    /**
     * Counts the verses (= input fields in the current stanza
     * @returns {number}
     */
    countFields() {
        return this.children.length;
    }
}
