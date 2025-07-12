import {BaseNode} from "../API.js";
import {Select} from "./2_Select.js";

export class Parambox extends BaseNode {
     constructor({selector = "#parambox", addButtons = false, events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({
            selector, addButtons, addButtons, tag: "div", id, events, buttons
        });
        // Now `this.el` is set and registered.
        Parambox.instance = this;
    }

    addSelect({ selector = null, id = null, events = {}, buttons = {} } = {}) {
        return new Select({selector});
    }
}