import {getRhymeScheme, setRhymeScheme} from './main.js';
import {flashMessage} from './niftyThings.js';

let tmpCounter = 0;
/** Creat an event handler for the sandbox */
const sandbox = document.getElementById('sandbox');
sandbox.addEventListener('click', onSandboxClick);

/**
 * Create or reuse a stanza, then append a verse-wrapper + input (+ buttons).
 */
export function addField(container, {
    id = null,
    text = '',
    buttonConfigs = [],    // [{ imgSrc, alt, onClick }]
    inputEvents = {}     // { eventName: handlerFn }
} = {}) {
    // 1) find or create the stanza (creation only in an empty sandbox)
    const stanza = container.lastStanza() || container.addStanza();

    // 2) build wrapper & input
    const wrapper = document.createElement('div');
    wrapper.classList.add('verse-wrapper');

    // 3.1) build the input element
    const input = document.createElement('input');
    input.id = id || `tmp-verse-${++tmpCounter}`;
    input.value = text;
    input.classList.add('verse');
    // 3.2 wire up any passed-in input events
    for (const [evt, handler] of Object.entries(inputEvents)) {
        input.addEventListener(evt, handler);
    }
    // 3.3) add the input to the wrapper
    wrapper.appendChild(input);

    // 4) add optional buttons to the wrapper
    buttonConfigs.forEach(cfg => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.classList.add('field-btn');
        const img = document.createElement('img');
        img.src = cfg.imgSrc;
        img.alt = cfg.alt || '';
        btn.appendChild(img);
        if (typeof cfg.onClick === 'function') {
            btn.addEventListener('click', cfg.onClick);
        }
        wrapper.appendChild(btn);
    });

    // 5) attach & focus
    stanza.appendChild(wrapper);
    input.focus();

    return wrapper;
}

// ==== Prototype patches for fluent API ====
/** container.addField(opts) */
HTMLElement.prototype.addField = function (opts) {
    return addField(this, opts);
};

/** Click handler for the sandbox.
 * @param {MouseEvent} e *
 */
function onSandboxClick(e) {
    const target = e.target;
    if (target == sandbox) { // clicked in an empty area of the sandbox
        // put focus on the last stanza's last input
        const stanzas = sandbox.querySelectorAll(':scope>.stanza-wrapper');
        if (stanzas) {
            const verses = stanzas[stanzas.length-1].querySelectorAll('.verse-wrapper>input.verse');
            if (verses) verses[verses.length-1].focus();
        }
        return;
    }
}

/**
 * Keydown handler for any verse-input.
 * - Enter/Tab on nonempty => new field
 * - Enter/Tab on empty    => move this field into a new stanza
 */
export function handleFieldKeydown(e) {
    if (!['Enter', 'Tab'].includes(e.key)) return;
    e.preventDefault();

    const input = e.target;
    const container = input.closest('#sandbox');
    const wrapper = input.parentElement;

    if (input.value.trim()) {
        // nonempty: spawn a fresh field in the (new or same) stanza
        const rhymeScheme = getRhymeScheme();
        if ((rhymeScheme.elements.length == 0) ||
            (locateInRhymeScheme(container, input) < rhymeScheme.elements.length - 1)) {
            if (container.allowNewStanza(input)) {
                container.addStanza()
            }
            container.addField({
                inputEvents: {keydown: handleFieldKeydown}
            });
        }
    } else {
        // empty: move this wrapper into its own new stanza
        if (container.allowNewStanza(input)) {
            // If the rhyme scheme allows a new stanza, we create it
            // and move the wrapper with the empthy field into it.
            const newStanza = container.addStanza();
            newStanza.appendChild(wrapper);
            input.focus();
        } else {
            flashMessage(input.closest('.verse-wrapper'),
                'An empty line is not allowed here');
            return;
        }
    }
}

/** Walks through the rhyme scheme and the content of the sandbox
 *  and returns true if the next line belongs in a new stanza
 * @param container
 * @param input
 * @param rhymeScheme
 * @return {boolean}
 */
function allowNewStanza(container, input, rhymeScheme = getRhymeScheme()) {
    // 1) Return the lines as defined in the rhyme scheme
    const lines = Array.isArray(rhymeScheme?.elements) ? rhymeScheme.elements : [];
    // 2) If the rhyme scheme is empty, we can allow a new stanza when the input is empty,
    //    bout only if the stanza contains more than this empty field
    if (lines.length === 0) {
        if (input.value.trim() === '') {
            const wrapper = input.parentNode;
            return wrapper.nextSibling || wrapper.previousSibling ? true : false;
        } else { //if (input.value.trim() !== ''
            return false;
        }
    }

    // 3) Loop through the rhyme scheme and the container in parallel
    let lineNr = locateInRhymeScheme(container, input); // this will be the index of the current line in the rhyme scheme
    // --> at this point, lineNr is the index of the current line in the rhyme scheme

    // 4) Now we can do checks on line[lineNr] in the rhyme scheme and the content of the input
    //   - If we are past the last line in the rhyme scheme, we can allow a new stanza
    if (lineNr >= lines.length) return false;
    if (input.value.trim()) {
        // If the input is not empty, look whether the line in the rhyme scheme is empty
        const thisRhyme = lines[lineNr].line?.txt ?? '';
        const nextRhyme = lineNr + 1 < lines.length ? lines[lineNr + 1].line?.txt ?? '' : undefined;
        //   - If the input is empty and the corresponding line in the rhyme scheme is empty,
        //     we can allow a new stanza
        if (input.value.trim() === '') return thisRhyme === '';
        //   - If the input field has content and the next line in the rhyme scheme is empty,
        //
        return nextRhyme === '';
    }
}

HTMLElement.prototype.allowNewStanza = function (input) {
    return allowNewStanza(this, input);
};

/** Walks through the current input and determines the corresponding line number in the rhyme scheme.
 * @param container
 * @param input the input element that currently has the focus
 * @return lineNr the index of the current line in the rhyme scheme
 * */
function locateInRhymeScheme(container, input) {
    let lineNr = 0; // this will be the index of the current line in the rhyme scheme
    outer:
        for (const stanza of container.children) {
            for (const verse of stanza.children) {
                if (verse.firstChild === input) {
                    // here we have reached the current verse field and we know the corresponding position in the rhyme scheme
                    break outer;
                }
                lineNr++;
            }
            lineNr++;
        }
    // --> at this point, lineNr is the index of the current line in the rhyme scheme
    return lineNr;
}

/** Adds a new stanza to the sandbox
 * @param id
 * @return stanza
 * */
export function addStanza(container, {
    id = null,
    className = 'stanza-wrapper'
} = {}) {
    const stanza = document.createElement('div');
    stanza.classList.add(className);
    stanza.id = id || `tmp-stanza-${++tmpCounter}`;
    container.appendChild(stanza);
    return stanza;
}

HTMLElement.prototype.addStanza = function (opts) {
    return addStanza(this, opts);
};

/** looks for the last stanza in the sandbox
 * @return stanza
 * */
export function lastStanza(container, {
    className = 'stanza-wrapper'
} = {}) {
    const all = container.querySelectorAll(`.${className}`);
    return all[all.length - 1] || null;
}

HTMLElement.prototype.lastStanza = function (opts) {
    return lastStanza(this, opts);
};
