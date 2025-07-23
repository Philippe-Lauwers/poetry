import {activateParambox, deactivateParambox, getRhymeScheme} from './paramboxInteraction.js';
import {BaseNode} from './API.js';
import {Poem} from './sandboxAPI/1_Poem.js';
import {Stanza} from './sandboxAPI/2_Stanza.js';
import {VerseWrapper} from './sandboxAPI/3_VerseWrapper.js';
import {Verse} from './sandboxAPI/4_Verse.js';
import {Suggestionbox} from "./suggestionboxAPI/1_SuggestionBox.js";
import {activateSuggestionbox} from "./suggestionboxInteraction.js";
import {flashMessage} from './niftyThings.js';

/**
 *Create a single shared instance of the sandbox */
let sandbox = null;

/**
 * Read-only accessor for any code that merely needs to *use*
 * the existing poem.  Will be `null` until initSandbox() runs.
 */
export const getSandbox = () => Poem.instance;

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
        const verse = wrapper?.firstChild; // anything appearing after the verse in the wrapper is a button
        verse?.el.focus();
    }
}

/**
 * Handlers for keyboard interaction: Enter, Tab, ArrowUp, ArrowDown
 * @param e
 */
export function verseKeydown(e) {
    let actionCaught = false;
    switch (e.key) {
        case 'Backspace':
        case 'Delete':
        case 'Spacebar':
        case ' ':
            setTitlePlaceholder(e.target)
            break;
        case 'Enter':
        case 'Tab':
            setTitlePlaceholder(e)
            actionCaught = verseAccept({myEvent: e});
            break;
        case 'ArrowUp':
            actionCaught = moveFocus(e, -1)
            break;
        case 'ArrowDown':
            actionCaught = moveFocus(e, 1)
            break;
        default:
            highlightIfEmpty(e);
            break;
    }
    if (actionCaught) {
        e.preventDefault();
    }
}
export function setTitlePlaceholder(myFld) {
    const poem = getSandbox();
    if (poem.firstChild.firstChild.firstChild === BaseNode.getWrapper(myFld)) {
                if (document.getElementById('poemTitle').value.trim() === '') {
                    document.getElementById('poemTitle').placeholder = myFld.value;
                }
    }
}
export function verseKeyup(e) {
    const poem = getSandbox();            // the Poem instance
    switch (e.key) {
        case ' ':
        case 'Enter':
        case 'Tab':
        case 'ArrowUp':
        case 'ArrowDown':
        default:
            highlightIfEmpty(e);
            disableGenBtn(e);
            break;
    }
}

/**
 * Keydown handler for verse-input Enter/Tab.
 * - Enter/Tab on nonempty => new field
 * - Enter/Tab on empty    => move this field into a new stanza
 */
export function verseAccept({myEvent = null, myVerse = null}) {
    let verse;
    if (myEvent) {
        verse = BaseNode.getWrapper(myEvent.target);}   // assuming BaseNode.registry
    else if (myVerse) {
        verse = myVerse;}
    const poem = getSandbox();                // Poem instance
    let stanza = poem.findStanzaOf(verse);
    const wrapper = verse.parent;                  // VerseWrapper instance
    const rhymeScheme = getRhymeScheme();
    if (!verse || !poem || !stanza) return true;        // safety

    if (verse.value.trim()) {
        // In case the field has a value, we do the following ...
        if (wrapper.nextSibling) {
            // Test if the stanza has a next field, if so put focus there (and do nothing else)
            wrapper.nextSibling.firstChild.el.focus(); // focus next verse if it exists
            focusToEmptyField(poem, rhymeScheme); // focus -> first empty field when all verse fields are present
            return true;
        } else if (wrapper.parent.nextSibling) {
            // Test if there is a following stanza, if so there will always be a first field in the stanza;
            // put focus there and do nothing else
            wrapper.parent.nextSibling.firstChild.firstChild.el.focus(); // focus first verse of next stanza
            focusToEmptyField(poem, rhymeScheme); // focus -> first empty field when all verse fields are present
            return true;
        }
        // nonempty: spawn a fresh field in the (new or same) stanza
        if (!poemComplete(poem, verse, rhymeScheme)) {
            // compare with rhymeScheme.elements.length - 1
            // -1 because we compare indexes with a length

            if (allowNewStanza(poem, verse, rhymeScheme)) {
                stanza = poem.addStanza()
            }
            const newVerse = stanza.addVerse({
                events:
                    // keydown: verseKeydown,
                    // change: highlightIfEmpty
                    verse.events

            });
            // When we create a new verse, we move the "generate verse" button from the current to the new verse
            // and match the id with the button next to it
            let btn = verse.el.nextSibling;
            while (btn) {
                if (btn.id.startsWith("btn_generateVerse")) {
                    poem.moveButton(btn, verse.parent, newVerse.parent);
                }// move the button
                btn = btn.nextSibling
            }// to the new verse wrapper

            newVerse.el.focus();
        } else { // there is a rhyme scheme and the number of fields matches the rhyme scheme
            focusToEmptyField(poem, rhymeScheme);
            let btn = verse.el.nextSibling;
            while (btn) {
                if (btn.id.startsWith("btn_generateVerse")) {
                    if (typeof newVerse !== 'undefined') {
                        poem.moveButton(btn, verse.parent, newVerse.parent);
                    } else {
                        poem.removeButton(btn);
                    }
                }// move the button
                btn = btn.nextSibling
            }
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

/**
 * Method to highlight an emtpy field if
 * @param e target of an event, called at the change event of a field
 */
let _paramboxActive = true;
export function highlightIfEmpty(e) {
    if (e.target.value.trim() === '') {
        e.target.classList.add('verseEmpty');
    } else {
        e.target.classList.remove('verseEmpty');
        if (_paramboxActive) {
            // If parambox is active, deactivate it and remember it is deactivated
            // when the user has written some initial text
            deactivateParambox()
            _paramboxActive = false;
        }
    }
}

export function disableSandbox() {
    const fldSet = document.getElementById("sandboxFields")
    // const fldSetStatus = fldSet.getAttribute('disabled')
    // fldSet.setAttribute('disabled',true)
    const elements = fldSet.querySelectorAll('input[id^="v-"], button')
    elements.forEach(el => {
        if (el.tagName === 'INPUT') {
            el.readOnly = true;
        } else if (el.tagName === 'BUTTON') {
            el.disabled = true;
        }
    });
}
export function enableSandbox() {
    const fldSet = document.getElementById("sandboxFields")
    // const fldSetStatus = fldSet.getAttribute('disabled')
    // fldSet.removeAttribute('disabled')
    const elements = fldSet.querySelectorAll('input[id^="v-"], button')
    elements.forEach(el => {
        if (el.tagName === 'INPUT') {
            el.readOnly = false;
        } else if (el.tagName === 'BUTTON') {
            el.disabled = false;
        }
    });
}

/**
 * Disables/activates the generate verse button when the input field next to it has a value
 * @param e
 */
export function disableGenBtn(e, {includeFld = false} = {}) {
    const poem = getSandbox();
    let fld;
    let val;
    if (e.target.tagName === "INPUT") {
        fld = e.target
        val = fld.value
    } else {
        fld = poem.firstChild.firstChild.firstChild.el;
        // trick the following script into believing the field is not empty
        // because we are generating content for an empty verse but still want the button disabled
        val = "Clicked a submit button";
    }
    // Activate/desactivate the "generate verse" button according to the content of the verse field
    if(fld.nextSibling) {
        if(fld.nextSibling.id.startsWith("btn_generateVerse")) {
            fld.nextElementSibling.disabled = (val !== '')
            if (includeFld) fld.readOnly = (val !== '')
        }
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
            return !!wrapper.prevSibling;
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
 * @param poem
 * @param verse the input element that currently has the focus
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

export function poemComplete(poem, verse, rhymeScheme = getRhymeScheme()) {
    if(rhymeScheme.elements.length == 0) {
        document.getElementById("btn_savePoem").removeAttribute("disabled");
        document.getElementById("chckBx_final").removeAttribute("disabled");
        return false;
    };
    // -1 because we compare indexes with a length
    if(locateInRhymeScheme(poem, verse) < rhymeScheme.elements.length - 1) {
        document.getElementById("btn_savePoem").removeAttribute("disabled");
        return false;
    };
    document.getElementById("btn_savePoem").removeAttribute("disabled");
    document.getElementById("chckBx_final").removeAttribute("disabled");
    return true;
}

/**
 * Places the focus on the first empty field if there is one and adapts the css class
 * @param poem
 * @param rhymeScheme
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
export function firstEmptyVerse(poem) {
    for (const stanza of poem.children) {
        if (!stanza.children) {
            return null
        }
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

/**
 * Looks for the next verse of the poem, if there is one.
 * @param verse
 * @return Verse object || null
 */
function nextVerse(verse) {
    if (verse.parent.nextSibling !== null) {
        return verse.parent.nextSibling.firstChild;
    }
    let stanza = verse.stanza().nextSibling
    if (stanza) {
        return stanza.firstChild.firstChild ? stanza.firstChild.firstChild : null;
    }
    return null
}


/**
 * This function enables disabled verses
 * - first verse = when a draft poem was automatically generated, generate verse button can be ditched
 * - last verse = when a single verse was requested
**/
function activateVerses(poem) {
    for (const stanza of poem.children.filter(s => (s.constructor.name === "VerseWrapper"))) {
        for (const wrapper of stanza.children) {
            // wrapper.firstChild is the Verse instance for that <input>
            const verse = wrapper.firstChild;
            verse.el.readOnly = false;// enable empty verses
            verse.className = "verse";
            let btn = verse.el.nextSibling;
            while (btn) {
                btn.disabled = false;
                btn = btn.nextSibling;
            }
        }
    }
    poem.firstChild.firstChild.firstChild.el.readOnly = false;
    poem.firstChild.firstChild.firstChild.className = "verse";
    enableSandbox()
}

/** This function removes all buttons with the given prefix from the verse wrappers
 *  * @param pref
 */
function removeButtons(pref = "btn_generateVerse") {
    // remove the generate verse button from the previous verse wrapper
    const sandbox = getSandbox();
    for (let stanza of sandbox.children) {
        for (let wrapper of stanza.children) {
            for (let btn of wrapper.el.childNodes) {
                if (btn.id.startsWith(pref)) {
                    wrapper.removeButton(btn);
                }
            }
        }
    }
}

/**
 * This function is called when the poem is received from the backend, it is only accessible when
 * the sandbox is empty (i.e., there is a stanza>>versewrapper>>verse but the verse is empty
 * It creates stanzas and verse fields according to the poem object
 * @param poem
 * @returns null
 */
export function receivePoem(poem) {
    const sandbox = getSandbox();
    const rhymeScheme = getRhymeScheme();
    let myVerse;
    let myStanza;
    const myStructPoem = document.getElementById("struct-sandbox");
    let myStructStz;
    let myStructVw;
    let myStructV;

    if (!document.getElementById("poem_id")) {
        const idFld = document.createElement("input");
        idFld.id = idFld.name = "poem_id"
        idFld.type="hidden"
        idFld.value = poem.id
        document.getElementsByClassName("top-pane")[0].append(idFld)
    }

    // If the first verse is also the first empty verse, we know a full poem or a requested first verse is received
    // (the button is otherwise deactivated
    let FEV = firstEmptyVerse(sandbox)
    const FV = sandbox.firstChild.firstChild.firstChild;
    let isFullPoem = (FEV === FV)
    poem.stanzas.forEach((s, stanzaIndex) => {
        let {id, oldId, verses} = s.stanza;
        let stanzaEl;

        if (isFullPoem && stanzaIndex === 0) {
            stanzaEl = document.getElementById(sandbox.findStanzaOf(FV).id);
        } else {
            stanzaEl = document.getElementById(Stanza.formatID({id: id, prefix: "s-"}));
        }

        if (stanzaEl) { // The stanza is already present in the DOM, get a handle to it
            myStanza = BaseNode.getWrapper(stanzaEl);
            if (isFullPoem && stanzaIndex === 0) {
                // If the stanza is the first stanza of a full poem, we need to update the id and the struct fields
                const oldStzId = myStanza.id;
                myStanza.id = Stanza.formatID({id: id, prefix: "s-"});
                myStructStz = document.getElementById("struct-"+oldStzId);
                myStructPoem.value = myStructPoem.value.replace(oldStzId, myStanza.id);
                myStructStz.id = "struct-" + myStanza.id;
                myStructStz.name = myStructStz.id
            }
        } else {
            stanzaEl = document.getElementById(oldId);
            if (stanzaEl) { // The stanza was found by the oldId, so we need to update the id and the struct fields
                myStanza = BaseNode.getWrapper(stanzaEl);
                const oldStzId = myStanza.id;
                myStructStz = document.getElementById(("struct-" + myStanza.id));
                // Stanza found by oldId, so we need to update the id and the struct fields
                myStanza.id = Stanza.formatID({id: id, prefix: "s-"});
                myStructPoem.value = myStructPoem.value.replace(oldStzId, myStanza.id);
                myStructStz.id = "struct-" + myStanza.id;
                myStructStz.name = myStructStz.id;
            } else { // The stanza is not present in the DOM - neither by id nor by oldId - so we create one
                const newStzId = Stanza.formatID({id: id, prefix: "s-"});
                myStanza = sandbox.addStanza({id: newStzId});
                // struct fields are updated in the stanza constructor
                // but we still set a handle ready for handling the verses
            }
        }
        myStructStz = document.getElementById("struct-" + myStanza.id);

        s.stanza.verses.forEach((v, verseIndex) => {
            let {text, id, oldId, suggestions} = v.verse;
            let verseEl

            if (isFullPoem && stanzaIndex === 0 && verseIndex === 0) {
                verseEl = document.getElementById(FV.id);
                // Now tha we have grabbed the first verse, set the placeholder of the title field to the first verse
            } else {
                verseEl = document.getElementById(Verse.formatID({id: id, prefix: "v-"}));
            }

            if (verseEl) { // The verse is already present in the DOM, get a handle to it ...
                myVerse = BaseNode.getWrapper(verseEl);
                myVerse.value = (myVerse.value !== text) ? text : myVerse.value;
                setTitlePlaceholder(verseEl)

                if (suggestions) {
                    const SB = new Suggestionbox({
                        selector: Verse.formatID({id: id, prefix: "suggB-v-"}),
                        id: Verse.formatID({id: id, prefix: "suggB-v-"}),
                        verse: myVerse,
                        location: myVerse.stanza,
                        suggestions: suggestions
                    });
                    activateSuggestionbox();}
                if (isFullPoem && stanzaIndex === 0 && verseIndex === 0) {
                    oldId = myVerse.id
                    const oldVwId = myVerse.parent.id;
                    myVerse.id = Verse.formatID({id: id, prefix: "v-"});
                    myVerse.name = myVerse.id;
                    myVerse.parent.id = VerseWrapper.formatID({id: id, prefix: "vw-"});
                    // Update the structure fields
                    myStructV = document.getElementById("struct-" + oldId);
                    myStructVw = document.getElementById("struct-" + oldVwId);

                    myStructV.id = "struct-" + myVerse.id;
                    myStructV.name = myStructV.id;
                    myStructVw.value = myStructVw.value.replace(oldId, myVerse.id);
                    myStructVw.id = "struct-" + myVerse.parent.id;
                    myStructVw.name = myStructVw.id;
                    myStructStz.value = myStructStz.value.replace(oldVwId, myVerse.parent.id);
                }// ... and set the value if changed
            } else { // The verse can not be found by id
                // 1. We search by oldId which is the id of the verse in the old poem
                verseEl = document.getElementById(oldId);
                // 2. If the verse is not found by id or oldId,the user might have clicked the "generate verse" button
                //    which only is accessible when the verse is empty
                if (!verseEl) {
                    verseEl = firstEmptyVerse(sandbox)?.el??null;
                }

                if (verseEl) { // The verse was found by the oldId, so we need to update the id and the struct fields
                    // Update the verse id, name and value
                    oldId = verseEl.id;
                    myVerse = BaseNode.getWrapper(verseEl);
                    myVerse.id = Verse.formatID({id: id, prefix: "v-"});
                    myVerse.name = myVerse.id;
                    myVerse.value = (myVerse.value !== text) ? text : myVerse.value;
                    if (suggestions) {
                        const SB = new Suggestionbox({
                            selector: Verse.formatID({id: id, prefix: "suggB-v-"}),
                            id: Verse.formatID({id: id, prefix: "suggB-v-"}),
                            verse: myVerse,
                            location: myVerse.stanza,
                            suggestions: suggestions
                        });
                        activateSuggestionbox();
                    }
                    // Update the verse wrapper id
                    let  myVerseWrapper = myVerse.parent;
                    let oldVwId = myVerseWrapper.id;
                    myVerseWrapper.id = VerseWrapper.formatID({id: id, prefix: "vw-"});
                    // Update the structure fields
                    myStructV = document.getElementById("struct-" + oldId);
                    myStructVw = document.getElementById("struct-" + oldVwId);

                    myStructStz.value = myStructStz.value.replace(oldVwId, myVerseWrapper.id);
                    myStructVw.value = myStructVw.value.replace(oldId, myVerse.id);
                    myStructVw.id = "struct-" + myVerseWrapper.id;
                    myStructVw.name = myStructVw.id;
                    myStructV.id = "struct-" + myVerse.id;
                    myStructV.name = myStructV.id;
                } else { // The verse can neither be found by id, nor by oldId
                      // This scenario occurs when we are loading a full poem and are beyond the first verse
                        let events = myVerse.events || {};
                        // Look for the generate verse button in the verse wrapper
                        let myBtn
                        for (let btn of myVerse.parent.el.childNodes) {
                            if (btn.id.startsWith("btn_generateVerse")) {
                                myBtn = btn;
                                break;
                            }
                        }
                        const myNewVerse = myStanza.addVerse({
                            id: id,
                            value: text,
                            events: events,
                        });
                        // Move the generate verse button to the new verse wrapper
                        if (myBtn) {
                            sandbox.moveButton(myBtn, myVerse.parent, myNewVerse);
                        }
                        myVerse = myNewVerse;
                }
            }
        });
    });
    if (poemComplete(sandbox,myVerse,getRhymeScheme())) {
        removeButtons("btn_generateVerse");
    }
    activateVerses(getSandbox())
    enableSandbox()
    activateParambox()
    verseAccept({myVerse: myVerse})
}