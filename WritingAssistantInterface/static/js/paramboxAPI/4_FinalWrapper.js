import {BaseNode} from "../API.js";
import {FinalCheckbox} from "./5_2_FinalCheckbox.js";
import {FinalLabel} from "./5_1_FinalLabel.js";
import {getParambox, toggleSaveButton} from "../paramboxInteraction.js";

export class FinalWrapper extends BaseNode {

    constructor({selector = null, id = "", events = {}, buttons = {}} = {}) {
        super({
            selector, id, tag: "div", className: "savePoem-wrapper", events, buttons
        }); // Now `this.el` is set and registered.
        this._btn = this.el.firstChild
        this.addCheckbox({id:"chckBx_"+this.id, value:2})
        this.addLabel({id: "lbl_" + this.id, htmlFor: "chckBx_" + this.id});
    }


    addCheckbox({id="", value= 2} = {}) {
        const F = new FinalCheckbox({
            // value = 1: draft, value = 2: final so we take 2 as value for the checkbox
            // which is passed to the backend as status
            id: id, value: value, events: {
                change: e => toggleSaveButton(e, e.target, {saveBtn: this._btn})}
            });
        return this.insertBefore(F,this._btn);
    }


    addLabel({id = "", htmlFor = ""} = {}) {
        const L = new FinalLabel({id: "label_" + this.id, htmlFor: "chckBx_" + this.id, labelText: "Final"})
        return this.insertBefore(L, this._btn);
    }

    addEdit() {
        const parambox = getParambox();
        const checkbox = document.getElementById("chckBx_final");
        if (this.firstChild.el.checked && !document.getElementById("btn_editPoem")) {
            this.addButton({
                    id: "btn_editPoem",
                    value: 1,
                    type: "submit",
                    formaction: "/editPoem",
                    formmethod: "post",
                    className: "btn",
                    alt: "Edit poem"
                }
            )
            document.getElementById("btn_savePoem").style.display = "none";
            for (let el of parambox.children) {
                if (el.id!=="btn_editPoem" && el.id!=="chckBx_final" && el.id!=="final") {
                    console.log("Disabling element",el.id)
                    el.disabled=true;
                }
            }
            checkbox.addEventListener('click', this.blockCheckbox);
            checkbox.classList.add("read-only");
        } else {
            this.removeButton("btn_editPoem");
            const saveBtn = document.getElementById("btn_savePoem")
            saveBtn.style.display = "inline-block";
            saveBtn.removeAttribute("disabled")
        for (let el of parambox.children) {
                el.disabled=false;
            }
            checkbox.removeEventListener('click', this.blockCheckbox);
            checkbox.classList.remove("read-only");
        }
    }
    blockCheckbox = e => e.preventDefault();
}
