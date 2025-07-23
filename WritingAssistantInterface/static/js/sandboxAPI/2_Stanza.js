/** Add a new stanza and return the Stanza wrapper */
import {BaseNode} from "../API.js";
import {VerseWrapper} from "./3_VerseWrapper.js";
import {Verse} from "./4_Verse.js";

export class Stanza extends BaseNode {
    static #nStanza = 0;

    constructor({selector = null, id = null, events = {}, buttons = {}} = {}) {
        const isNew = id == null;
        const serial = isNew ? ++Stanza.#nStanza : id;
        const finalID = Stanza.formatID({id: serial, prefix: "s-", suffix: isNew ? "-tmp" : ""});
        super({
            id: finalID, tag: "div", className: "stanza-wrapper", events, buttons
        }); // Now `this.el` is set and registered.
        Stanza.instance = this;
    }

    /**
     * Add a new verseWrapper and return the verseWrapper wrapper */
    addVerseWrapper({id = null, events = {}, buttons = {}} = {}) {
        const vw = new VerseWrapper({id:id, buttons:buttons})
        return this.append(vw);
    }
    /**
     * Add a new Verse ( = create new verseWrapper and append a new verse) */
    addVerse({id = null, value= "", events = {} , buttons = {}} = {}) {
        const vw = new VerseWrapper({ id:id, buttons: buttons});
        const v = vw.addVerse({id: id, value: value, events: events});
        this.append(vw);
        return v;
    }

    /**
     * Function that returns the first field of the stanza
     */
    firstVerse() {
        return this.firstChild.firstChild;
    }
    /**
     * Function that returns the last field of the stanza
     */
    lastVerse() {
        return this.lastChild.lastChild;
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
