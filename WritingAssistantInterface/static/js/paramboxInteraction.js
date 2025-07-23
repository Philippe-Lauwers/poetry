import {Parambox} from './paramboxAPI/1_Parambox.js';
import {retrieveRhymeScheme} from "./linkUserInteractionToBackend.js";
import {firstEmptyVerse, getSandbox} from "./sandboxInteraction.js";

export const getParambox = () => Parambox.instance;

export function loadParambox() {
    // Select boxes are generated in index.html using jinja
    // We create wrapper objects for storing additional parameters
    // and add an event listener to the select boxes
    const parambox = getParambox();            // the Poem instance
    if (!parambox) return;                    // safety guard
    const paramboxEL = parambox.el;

    paramboxEL.querySelectorAll("select").forEach(selectEl => {
        const sel = parambox.addSelect({ selector: selectEl });
        sel.el.addEventListener("change", e => {
            firstEmptyVerse(getSandbox())?.el.focus();
        });
        Array.from(selectEl.options).forEach(optEl => {
        sel.addOption({ selector: optEl })
        });
    });
    // Add a submit button and a checkbox to indicate the poem is final
    parambox.addFinal({
        id: "final", label:"Final", buttons: {
            btn_finalPoem: {
                id: "btn_savePoem",
                type: "submit",
                formaction: "/savePoem",
                formmethod: "post",
                value:1,
                className: "btn",
                alt: "Save the draft"
            }
        }
    })
    document.getElementById("btn_savePoem").disabled = true;
}

/**
 * Called after a submit that fetches an entire poem
 * Removes entries from select that are not suited (keeps only the persistent options and the currently selected)
 * @param e
 * @param submitter
 */
export function deactivateParambox(e=null, submitter=null) {
    const parambox = getParambox();
    let hasPersistentOption;
    // loop through selects
    for (let sel of parambox.children) {
        // Check whether one of the options is persistent (i.e. remains available when an option is selected)
        hasPersistentOption = false;
        if (sel.el.nodeName === "SELECT") {
            for (let opt of sel.children) {
                if (opt.persistence) {
                    hasPersistentOption = true;
                    break;
                } else if (opt.el.value !== sel.el.value) {
                    opt.el.disabled = true;
                }
            }
        }
        // If there are no persistent options, don't disable the select but remove the non-persistent options
        if (!hasPersistentOption) {
            mockDisableSelect(sel.el);
        } else {
            for (let opt of sel.children) {
                if (!opt.persistence && sel.el.value !== opt.el.value) {
                    opt.remove();
                }
            }
        }
        if (submitter) {
            submitter.disabled = true;
        }
    }
    document.getElementById("btn_generatePoem").disabled = true;
}
export function activateParambox() {
    document.getElementById("btn_savePoem").removeAttribute("disabled");
}
export function deactivateFinal() {
    document.getElementById("btn_savePoem").disabled = true;
    document.getElementById("chckBx_final").el.disabled = false;
    deactivateParambox()
    getParambox()
}
export function mockDisableSelect(el) {
    const myEl = (typeof el ==="string") ? document.getElementById(el) : el;
    myEl.classList.add('read-only-select');
    myEl.setAttribute('aria-disabled', 'true');
    myEl.setAttribute('tabindex', '-1');
    myEl.addEventListener('keydown', preventChange);
    myEl.addEventListener('focus', preventChange);
}
export function mockEnableSelect(el) {
    const myEl = (typeof el ==="string") ? document.getElementById(el) : el;
    myEl.classList.remove('read-only-select');
    myEl.removeAttribute('aria-disabled');
    myEl.removeAttribute('tabindex');
    myEl.removeEventListener('keydown', preventChange);
    myEl.removeEventListener('focus', preventChange);
}
function preventChange(e) {
    e.stopImmediatePropagation();
    e.preventDefault();
}

/**
 * Is called when the form is loaded (with lang and rhymescheme the initial values)
 * and when the user chooses another rhymescheme
 * @param lang
 * @param rhymeScheme
 */
let _poemDesc

export async function receiveRhymeScheme() {
    try {
        const json = await retrieveRhymeScheme();
        _poemDesc = json.rhymeScheme ? json : null;
        // Disable the generate button if there are no elements in the rhyme scheme
        if (_poemDesc.rhymeScheme.elements.length === 0) {
            document.getElementById("btn_generatePoem").disabled = true;
        } else {
            document.getElementById("btn_generatePoem").disabled = false;
        }
        // …do something with _poemDesc…
    } catch (err) {
        console.error('Failed to get rhyme scheme:', err);
    }
    return _poemDesc;
}
export function getRhymeScheme() {
    return _poemDesc !== undefined ?_poemDesc.rhymeScheme: null;
}

/**
 * Function to toggle the alt- and title-attributes of the save button */
export function toggleSaveButton(e, target, {saveBtn = null}) {
    saveBtn.alt = saveBtn.title === "Save the draft" ? "Save the final version" : "Save the draft";
    saveBtn.title = saveBtn.title === "Save the draft" ? "Save the final version" : "Save the draft";
}