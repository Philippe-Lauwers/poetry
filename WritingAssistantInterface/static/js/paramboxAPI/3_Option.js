import {BaseNode} from "../API.js";

export class Option extends BaseNode {

    constructor({selector = null, id = "", value=null, label=null, events = {}, buttons = {}} = {}) {
        super({
            selector, id, tag: "option", events, buttons
        }); // Now `this.el` is set and registered
        this.el.value = this.el.value !==""? this.el.value:value;
        this.el.innerHTML = this.el.innerHTML !==""? this.el.innerHTML:label;

         this.persistence = null; // We either set this by value or force lookup by setting to null
    }

    get persistence() {
        return this._persistence;
    }
    set persistence(value) {
        if (value === null) {
            for (let RS of rhymeSchemes.options) {
                if ('form_'.concat(RS.id) == this.id) {
                    this._persistence = RS.persistent;
                    break;
                }
            }
        } else {
            this._persistence = value;
        }
    }
}
