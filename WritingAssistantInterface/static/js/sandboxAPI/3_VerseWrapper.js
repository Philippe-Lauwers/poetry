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
    addVerse({selector = null, id = null, value = "", events = {}} = {}) {
        // append a new verse (necessary to create the fields that store the id's of the poem in a structure
        const v = this.append(new Verse({id: id, value: value, events: events}))
        // check if there is a button in front of the verse field, in that case move the button to the back
        for (let elem of this.el.children) {
            const elem_id = elem.id
            switch (elem_id.substring(elem_id.indexOf("-") + 1, elem_id.lastIndexOf("-"))) {
                case "gen-v":
                    this.el.insertBefore(v.el, elem)
                    break;
            }
        }
        return v;
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
