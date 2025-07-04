import {BaseNode} from './API.js';
import {Parambox} from './paramboxAPI/1_Parambox.js';
import {Select} from './paramboxAPI/2_Select.js';
import {Option} from './paramboxAPI/3_Option.js';
import {retrieveRhymeScheme} from "./linkUserInteractionToBackend.js";

export const getParambox = () => Parambox.instance;

export function loadParambox() {
    // Select boxes are generated in index.html using jinja
    // We create wrapper objects for storing additional parameters
    const parambox = getParambox();            // the Poem instance
    if (!parambox) return;                    // safety guard
    const paramboxEL = parambox.el;

    paramboxEL.querySelectorAll("select").forEach(selectEl => {
        const sel = parambox.addSelect({ selector: selectEl });
        Array.from(selectEl.options).forEach(optEl => {
        sel.addOption({ selector: optEl })
        });
    });
}

/**
 * Called after a submit that fetches an entire poem
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
            sel.el.disabled = true;
        } else {
            for (let opt of sel.children) {
                if (!opt.persistence && sel.el.value !== opt.el.value) {
                    opt.remove();
                }
            }
        }
        if (submitter) {
            submitter.disabled = true;
        } else {
            document.getElementById("btn_generatePoem").disabled = true;
        }
    }
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
    if (_poemDesc.rhymeScheme.elements.length === 0) {
        document.getElementById("btn_generatePoem").disabled = true;
    } else {
        document.getElementById("btn_generatePoem").disabled = false;
    }
    // …do something with _poemDesc…
  } catch (err) {
    console.error('Failed to get rhyme scheme:', err);
  }
}
export function getRhymeScheme() {
    return _poemDesc !== undefined ?_poemDesc.rhymeScheme: null;
}