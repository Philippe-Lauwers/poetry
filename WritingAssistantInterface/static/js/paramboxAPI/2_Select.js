import {BaseNode} from "../API.js";
import {Option} from "./3_Option.js";

export class Select extends BaseNode {

    constructor({selector = null, id = "", events = {}, buttons = {}} = {}) {
        super({
            selector, id, tag: "option", events, buttons
        }); // Now `this.el` is set and registered.

    }

    addOption({selector = null, id = "", value = null, label = null, events = {}, buttons = {} } = {}) {
        return new Option({selector, value, label})
    }
}
