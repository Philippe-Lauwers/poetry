/** Add a new stanza and return the Stanza wrapper */
import {BaseNode} from "../API.js";

export class Verse extends BaseNode {
    static #nVerse = 0;

    constructor({selector = null, id = null, value = "", events = {}, buttons = {}} = {}) {
        const isNew = id == null;
        const serial = isNew ? ++Verse.#nVerse : id;
        const finalID = Verse.formatID({id: serial, prefix: "v-", suffix: isNew ? "-tmp" : ""});
        super({
            id: finalID,
            name: finalID,
            tag: "input",
            type: "text",
            value: value,
            className: "verse",
            events
        });// Now `this.el` is set and registered.
        Verse.instance = this;
        this.el.name = this.el.id
    }

    /**
     *  === HELPER FUNCTIONS ===
     */
    get value() {
        return this.el.value;
    }
    set value(text) {
        this.el.value = text ?? "";
    }

    get stanza() {
        return this.parent.parent
    }
}
