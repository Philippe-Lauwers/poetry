import {BaseNode} from './API.js';
import {Parambox} from './paramboxAPI/1_Parambox.js';
import {Select} from './paramboxAPI/2_Select.js';
import {Option} from './paramboxAPI/3_Option.js';

export const getParambox = () => Parambox.instance;

export function loadParambox() {
    // Select boxes are generated in index.html using jinja
    // We create wrapper objects for storing additional parameters
    const parambox = getParambox();            // the Poem instance
    if (!parambox) return;                    // safety guard
    const paramboxEL = parambox.el;

    paramboxEL.querySelectorAll("select").forEach(selectEl => {
        const sel = parambox.addSelect({ selector: selectEl.id });
        Array.from(selectEl.options).forEach(optEl => {
        sel.addOption({ selector: optEl.id })
        });
    });
}
