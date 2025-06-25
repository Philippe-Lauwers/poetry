/** Wrapper class for the poem level
 * constructor
 * @param selector (id of the DOM-element)
 * @param events
 * @param buttons
 */
// poem.js
import {BaseNode} from "../API.js";
import {Stanza} from "./2_Stanza.js";


export class Poem extends BaseNode {

    constructor({selector = "#sandbox", events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({selector, tag: "div", id, events, buttons});
        // Now `this.el` is set and registered.
        Poem.instance = this;
    }

    /** Add a new stanza and return the Stanza wrapper */
    addStanza({id = null, events = {}, buttons = {}} = {}) {
        return this.append(new Stanza({id:id, events:events, buttons: buttons}));
    }

    /**
     * === HELPER METHODS/FUNCTIONS */
    /**
     * Function to find the stanza the specified verse belongs to
     * @param verse    BaseNode object representing a verse
     * */
    findStanzaOf(verse) {
        let node = verse;
        while (node && !(node instanceof Stanza)) node = node.parent;
        return node;
    }

    /**
     * Function that returns the first stanza of the poem
     */
    firstStanza() {
        return this.firstChild;
    }
    /**
     *  Function that returns the first field of the poem
     */
    firstField() {
        return this.firstStanza().firstField();
    }

    /**
     * Function that counts the number of inputfields (in reality the div-wrappers) in the poem
     * @returns {number}
     */
    countFields() {
        let cnt = 0;
        for (let stanza of this.children) {
            cnt += stanza.countFields();
        }
        return cnt;
    }
}
