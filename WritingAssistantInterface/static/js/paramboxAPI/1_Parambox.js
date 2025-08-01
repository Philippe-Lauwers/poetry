import {BaseNode} from "../API.js";
import {Select} from "./2_Select.js";
import {FinalWrapper} from "./4_FinalWrapper.js";
import {GoListWrapper} from "./6_GoListWrapper.js";

export class Parambox extends BaseNode {
     constructor({selector = "#parambox", addButtons = false, events = {}, buttons = {}} = {}) {
        const id = (typeof selector === "string")
            ? selector.replace(/^#/, "")
            : "";

        super({
            selector, addButtons, tag: "div", id, events, buttons
        });
        // Now `this.el` is set and registered.
        Parambox.instance = this;
    }

    addSelect({ selector = null, id = null, events = {}, buttons = {} } = {}) {
        return new Select({selector});
    }

    addFinal({selector = null, id=null, label="", chckBx=true, events = {}, buttons = {}} = {}) {
        const finalWrapper = new FinalWrapper({selector, id, events, buttons});
        this._finalWrapper = finalWrapper;
        return this.append(finalWrapper);
    }
    getFinal() {
         return this._finalWrapper
    }

    addGoList({selector = null, id = null, events = {}, buttons = {}} = {}) {
        const goListWrapper = new GoListWrapper({selector, id, events, buttons});
        return this.append(goListWrapper);
    }

}