import {BaseNode} from "../API.js";
import {FinalCheckbox} from "./5_2_FinalCheckbox.js";
import {FinalLabel} from "./5_1_FinalLabel.js";
import {getParambox, mockDisableSelect, toggleSaveButton} from "../paramboxInteraction.js";
import {editorProtected} from "../editorInteraction.js";
import {GoListLabel} from "./6_1_GoListLabel.js";

export class GoListWrapper extends BaseNode {

    constructor({selector = null, id = "", events = {}, buttons = {}} = {}) {
        super({
            selector, id, tag: "div", className: "goList-wrapper", events, buttons
        }); // Now `this.el` is set and registered.
        this._btn = this.el.firstChild
        this.addLabel({id: "lbl_" + this.id, htmlFor: "btn_" + this.id});
    }

    addLabel({id = "", htmlFor = ""} = {}) {
        const L = new GoListLabel({id: "label_" + this.id, htmlFor: "btn_" + this.id, labelText: "My overview"});
        return this.insertBefore(L, this._btn);
    }
}
