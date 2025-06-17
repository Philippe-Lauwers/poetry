import {getRhymeScheme, setRhymeScheme} from './main.js';
import {BaseNode, Poem, Stanza, VerseWrapper, Verse} from './sandbox.js';
import {flashMessage} from './niftyThings.js';

/**
 *Create a single shared instance of the sandbox */
let sandbox = null;

/**
 * Initialise (once) and return the Poem that wraps #sandbox.
 * Call this exactly once in your boot-strap code (e.g. main.js).
 */
export function initSandbox(selector = '#sandbox', opts = {}) {
    if (!sandbox) {
        sandbox = Poem.init(selector, opts);
    }
    return sandbox;
}

/**
 * Read-only accessor for any code that merely needs to *use*
 * the existing poem.  Will be `null` until initSandbox() runs.
 */
export const getSandbox = () => sandbox;


/**
 * Click handler for the sandbox.
 * @param {MouseEvent} e *
 */
export function sandboxClick(e) {
    const poem = getSandbox();            // the Poem instance
    if (!poem) return;                    // safety guard

    const rootEl = poem.el;               // actual <div id="sandbox">
    const target = e.target;

    /* Clicked an empty part of the sandbox? => look for the last field and focus*/
    if (target === rootEl) {
        const stanza = poem.lastChild;
        const wrapper = stanza?.lastChild;
        const verse = wrapper?.lastChild;
        verse?.el.focus();
    }
}

/**
 * Handler for keyboard interaction: Enter, Tab, ArrowUp, ArrowDown
 * @param e
 */
export function verseKeydown(e) {
    let actionCaught = false;
    switch (e.key) {
        case 'Enter':
        case 'Tab':
            actionCaught = verseAccept(e);
            break;
        case 'ArrowUp':
            actionCaught = moveFocus(e, -1)
            break;
        case 'ArrowDown':
            actionCaught = moveFocus(e, 1)
            break;
        default:
            break;
    }
    if (actionCaught) {
        e.preventDefault();
    }
}

/**
 * Keydown handler for verse-input Enter/Tab.
 * - Enter/Tab on nonempty => new field
 * - Enter/Tab on empty    => move this field into a new stanza
 */
function verseAccept(e) {
    const verse = BaseNode.getWrapper(e.target);   // assuming BaseNode.registry
    const poem = getSandbox();                // Poem instance
    let stanza = poem.findStanzaOf(verse);
    const wrapper = verse.parent;                  // VerseWrapper instance
    const rhymeScheme = getRhymeScheme();

    if (!verse || !poem || !stanza) return true;        // safety

    if (verse.value.trim()) {
        // In case the field has a value, we do the following ...
        if (wrapper.nextSibling !== null) {
            // Test if the stanza has a next field, if so put focus there (and do nothing else)
            wrapper.nextSibling.firstChild.el.focus(); // focus next verse if it exists
            focusToEmptyField(poem, rhymeScheme); // focus -> first empty field when all verse fields are present
            return true;
        } else if (wrapper.parent.nextSibling !== null) {
            // Test if there is a following stanza, if so there will always be a first field in the stanza;
            // put focus there and do nothing else
            wrapper.parent.nextSibling.firstChild.firstChild.el.focus(); // focus first verse of next stanza
            focusToEmptyField(poem, rhymeScheme); // focus -> first empty field when all verse fields are present
            return true;
        }
        // nonempty: spawn a fresh field in the (new or same) stanza
        if (rhymeScheme.elements.length == 0 ||
            locateInRhymeScheme(poem, verse) < rhymeScheme.elements.length - 2) {
            // compare with rhymeScheme.elements.length - 2
            // -1 because we compare indexes with a length
            // -1 because there will be no stanza separator at the end of the rhyme scheme

            if (allowNewStanza(poem, verse, rhymeScheme)) {
                stanza = poem.addStanza()
            }
            const newVerse = stanza.addVerse({
                inputEvents: {
                    keydown: verseKeydown,
                    change: highlightIfEmpty
                }
            });
            newVerse.el.focus();
        } else { // there is a rhyme scheme and the number of fields matches the rhyme scheme
            focusToEmptyField(poem, rhymeScheme);
        }
        return true;
    } else { // if (verse.value.trim() == '')
        // empty: move this wrapper into its own new stanza if a new stanza is allowed
        if (rhymeScheme.elements.length == 0 && allowNewStanza(poem, verse)) {
            // If the rhyme scheme allows a new stanza, we create it
            // and move the wrapper with the empty field into it.
            const newStanza = poem.addStanza();
            newStanza.append(wrapper);
            verse.el.focus();
            return true;
        } else {
            flashMessage(verse.parent,
                'An empty line is not allowed here');
            return true;
        }
    }
}

/**
 * Keydown handler for verse-input ArrowUp/ArrowDown.
 * @param e = the event
 * @param direction +1/-1 = down/up = next/previous field
 */
function moveFocus(e, direction) {
    const verse = BaseNode.getWrapper(e.target);   // assuming BaseNode.registry
    const poem = getSandbox();                // Poem instance
    let stanza = poem.findStanzaOf(verse);
    const wrapper = verse.parent;                  // VerseWrapper instance

    if (!verse || !poem || !stanza) return true;        // safety

    let newFocus = direction === 1 ? wrapper.nextSibling : wrapper.prevSibling;
    if (newFocus) {
        newFocus.firstChild.el.focus(); // newFocus = the wrapper
    } else {
        const newFocusStanza = direction === 1 ? stanza.nextSibling : stanza.prevSibling;
        if (newFocusStanza) {
            switch (direction) {
                case 1:
                    newFocus = newFocusStanza.firstChild.firstChild;
                    newFocus.el.focus();
                    break;
                case -1:
                    newFocus = newFocusStanza.lastChild.lastChild;
                    newFocus.el.focus();
                    break;
                default:
                    break;
            }
        }
    }
    return true;
}

let cntChanges = 0
export function highlightIfEmpty(e) {
    if (e.target.value.trim() === '') {
        e.target.classList.add('verseEmpty');
    } else {
             e.target.classList.remove('verseEmpty');
    }
}

/**
 * Checks if a new stanza may be added to the poem, according to the rhyme scheme
 * @param poem
 * @param verse
 * @param rhymeScheme
 * @returns {boolean|boolean}
 */
export function allowNewStanza(poem, verse, rhymeScheme = getRhymeScheme()) {
    // 1) Return the RSverses as defined in the rhyme scheme
    const RSverses = Array.isArray(rhymeScheme?.elements) ? rhymeScheme.elements : [];
    // 2) If the rhyme scheme is empty, we can allow a new stanza when the input is empty,
    //    but only if the stanza contains more than this empty field
    if (RSverses.length === 0) {
        if (verse.value.trim() === '') {
            const wrapper = verse.parent;
            return wrapper.prevSibling ? true : false;
        } else { //if (input.value.trim() !== ''
            return false;
        }
    }
    // 3) Loop through the rhyme scheme and the container in parallel
    let lineNr = locateInRhymeScheme(poem, verse); // this will be the index of the current line in the rhyme scheme
    // --> at this point, lineNr is the index of the current line in the rhyme scheme
    // 4) Now we can do checks on line[lineNr] in the rhyme scheme and the content of the input
    //   - If we are past the last line in the rhyme scheme, we can not allow a new stanza
    if (lineNr >= RSverses.length - 2) return false;
    // -1 because we compare indexes with a length
    // -1 because there will be no stanza separator at the end of the rhyme scheme
    const thisRhyme = RSverses[lineNr].verse?.txt ?? '';
    const nextRhyme = lineNr + 1 < RSverses.length ? RSverses[lineNr + 1].verse?.txt ?? '' : undefined;
    if (verse.value.trim()) {
        // If the input is not empty, look whether the line in the rhyme scheme is empty
        //   - If the input field has content and the next line in the rhyme scheme is empty,
        return nextRhyme === '';
    } else {
        //   - If the input is empty and the corresponding line in the rhyme scheme is empty,
        //     we can allow a new stanza
        return thisRhyme === '';
    }
}

/**
 *  Walks through the current input and determines the corresponding line number in the rhyme scheme.
 * @param container
 * @param input the input element that currently has the focus
 * @return lineNr the index of the current line in the rhyme scheme
 * */
export function locateInRhymeScheme(poem, verse) {
    let lineNr = 0; // this will be the index of the current line in the rhyme scheme

    outer:
        for (const stanza of poem.children) {
            for (const wrapper of stanza.children) {
                if (wrapper.firstChild === verse) {
                    // here we have reached the current verse field and we know the corresponding position in the rhyme scheme
                    break outer;
                }
                lineNr++;
            }
            // at this point, the stanza is complete, so we can add one to the line number
            lineNr++;
        }
    // --> at this point, lineNr is the index of the current line in the rhyme scheme
    return lineNr;
}

/**
 * places the focus on the first empty field if there is one and adapts the css class
 * @param poem
 * @return [no return]*/
function focusToEmptyField(poem, rhymeScheme) {
    const elems = rhymeScheme.elements;
    const cntRSVerses = elems
        .filter(el => el.verse.txt.trim() !== '')
        .length;
    if (cntRSVerses == poem.countFields()) {
        const emptyVerse = firstEmptyVerse(poem);
        if (emptyVerse !== null) {
            const emptyVerseEL = emptyVerse.el;
            emptyVerseEL.focus();
            flashMessage(emptyVerse.parent, "An empty line is not allowed here")
        }
    }
}
/**
 * Walks through the current input to look for the first empty field
 * @param poem
 * @return Verse object (if empty) */
function firstEmptyVerse(poem) {
    for (const stanza of poem.children) {
        for (const wrapper of stanza.children) {
            // wrapper.firstChild is the Verse instance for that <input>
            const verse = wrapper.firstChild;
            if (verse && verse.value === "") {
                return verse;
            }
        }
    }
    return null;
}

/** This function is called when the poem is received from the backend.
 * It creates stanzas and verse fields according to the poem object
 * @param poem
 * @returns null
 */
export function receivePoem(poem) {
    let txt = '';
    poem.stanzas.forEach((s, stanzaIndex) => {
        s.stanza.verses.forEach((v, verseIndex) => {
            txt += v.verse.text
            if (stanzaIndex < poem.stanzas.length - 1 || verseIndex < s.stanza.verses.length - 1) {
                ;
                txt += '\n';
            }
        });
        if (stanzaIndex < poem.stanzas.length - 1) {
            txt += '\n\n';
        }
    });
    alert(txt);
}