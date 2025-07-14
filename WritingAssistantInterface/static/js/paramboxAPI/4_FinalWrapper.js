import {BaseNode} from "../API.js";
import {FinalCheckbox} from "./5_2_FinalCheckbox.js";
import {FinalLabel} from "./5_1_FinalLabel.js";
import {toggleSaveButton} from "../paramboxInteraction.js";

export class FinalWrapper extends BaseNode {

    constructor({selector = null, id = "", events = {}, buttons = {}} = {}) {
        super({
            selector, id, tag: "div", className: "savePoem-wrapper", events, buttons
        }); // Now `this.el` is set and registered.
        this._btn = this.el.firstChild
        this.addCheckbox({id:"chckBx_"+this.id, value:1})
        this.addLabel({id: "lbl_" + this.id, htmlFor: "chckBx_" + this.id});
    }


    addCheckbox({id="", value= 1} = {}) {
        const F = new FinalCheckbox({
            id: "chckBx_" + this.id, value: 1, events: {
                change: e => toggleSaveButton(e, e.target, {saveBtn: this._btn})}
            });
        return this.insertBefore(F,this._btn);
    }


    addLabel({id = "", htmlFor = ""} = {}) {
        const L = new FinalLabel({id: "label_" + this.id, htmlFor: "chckBx_" + this.id, labelText: "Final"})
        return this.insertBefore(L, this._btn);
    }
}
