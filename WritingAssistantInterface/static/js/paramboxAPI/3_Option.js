import {BaseNode} from "../API.js";

export class Option extends BaseNode {

    constructor({selector = null, id = "", value=null, label=null, events = {}, buttons = {}} = {}) {
        super({
            selector, id, tag: "option", events, buttons
        }); // Now `this.el` is set and registered
        this.el.value = this.el.value !==""? this.el.value:value;
        this.el.innerHTML = this.el.innerHTML !==""? this.el.innerHTML:label;
    }
}
