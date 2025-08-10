import {Suggestionbox} from "./suggestionboxAPI/1_SuggestionBox.js";
import {Keywordbox} from "./keywordboxAPI/1_Keywordbox.js";
import {KeywordWrapper} from "./keywordboxAPI/4_1_KeywordWrapper.js";
import {Keyword} from "./keywordboxAPI/5_1_Keyword.js";
import {activateSuggestionbox} from "./suggestionboxInteraction.js";
import {flashMessage} from "./niftyThings.js";

/**
 * Read-only accessor for any code that merely needs to *use*
 * the existing poem.  Will be `null` until initSandbox() runs.
 */
export const getKeywordbox = () => Keywordbox.instance;

export function keywordKeydown(e, target) {
    let actionCaught = false;
    switch (e.key) {
        case 'Enter':
        case 'Tab':
            actionCaught = createNextKeyword({event: e, target: target});
            break;
        case 'ArrowUp':
            actionCaught = moveKeywordFocus(e, -1)
            break;
        case 'ArrowDown':
            actionCaught = moveKeywordFocus(e, 1)
            break;
        default:
            break;
    }
    if (actionCaught) {
        e.preventDefault();
    }
}

export function keywordKeyup(e, target) {
    switch (e.key) {
        case 'Enter':
        case 'Tab':
            break; // Handled in keydown
        case 'Backspace':
        case 'Delete':
        case ' ':
        case 'ArrowUp':
        case 'ArrowDown':
        default:
            disableKeywordGenBtn(e);
            break;
    }
}

export function createNextKeyword({event, target}) {
    const keywordBox = getKeywordbox();
    const keywordList = keywordBox.list;
    const targetWrapper = Keyword.getWrapper(target).parent;
    const targetId = target.id

    let Wr;  // <-- move declaration up so it's visible below

    if (target.value.trim() === "") {
        flashMessage(targetWrapper, 'Please fill out this keyword first');
    } else {
        const numChildren = keywordList.children.length;
        if (targetWrapper.nextSibling) {
            moveKeywordFocus(event, 1);
        } else if (numChildren > 0 && numChildren < keywordBox.n) {
            Wr = keywordList.addKeywordWrapper({
                buttons: targetWrapper.buttons,
                events: targetWrapper.events
            });
            const KwId = Wr.firstChild.id;
            for (const btn of Wr.el.children) {
                if (btn.id.startsWith("btn_del")) {
                    btn.value = KwId;
                    btn.style.setProperty("display", "none", "important");
                    btn.disabled = false;
                } else if (btn.id.startsWith("btn_random")) {
                    btn.value = KwId;
                    btn.style.setProperty("display", "inline-block", "important");
                }
            }
            Wr.firstChild.el.focus()
        }
    }
    return true; // action was caught
}

export function moveKeywordFocus(e, direction) {
    const current = e.target;
    const currentWrapper = Keyword.getWrapper(current);
    let nextWrapper;
    if (direction === 1) {
        nextWrapper = currentWrapper.parent.el.nextSibling;
    } else if (direction === -1) {
        nextWrapper = currentWrapper.parent.el.previousSibling;
    }

    if (nextWrapper) {
        const nextKeyword = nextWrapper.firstChild;
        nextKeyword.focus();
        return true; // action was caught
    } else {
        return false; // no action taken
    }
}


export function disableKeywordGenBtn(e) {
    const keywords = document.querySelectorAll('[id^="kw-"]');
    let disableGenBtn = true
    for (const kw of keywords) {
        if (kw.value.trim() !== "") {
            disableGenBtn = false
            break;
        }
    }
    activateKeywordbox({includeGenButton: disableGenBtn})
    const eventTargetId = e.target.id;
    const btnGen1 = document.querySelector(`button[id="btn_random1Keyword"][value="${eventTargetId}"]`)
    const btnDel1 = document.querySelector(`button[id="btn_deleteKeyword"][value="${eventTargetId}"]`)
    if (disableGenBtn) {
        btnGen1.disabled = false;
        btnGen1.style.display = "inline-block";
        btnDel1.disabled = true;
        btnDel1.style.display = "none"
    } else {
        btnGen1.disabled = true;
        btnGen1.style.display = "none";
        btnDel1.disabled = false;
        btnDel1.style.display = "inline-block"
    }
}

export function deactivateKeywordbox() {
    const keywordbox = getKeywordbox();
    keywordbox.header.disable();
    keywordbox.list.disable();
}

export function activateKeywordbox({includeGenButton = false} = {}) {
    const keywordbox = getKeywordbox();
    keywordbox.header.enable({includeGenButton});
    keywordbox.list.enable();
}

export function receiveKeywords(input) {
    const keywordBox = getKeywordbox();
    const keywordList = keywordBox.list;

    if (input.keywords) {
        const idFld = document.getElementById("poem_id")
        if (idFld.value == "") {
            idFld.value = input.id;
        }

        if (input.keywordSuggestions) { // If there are keyword suggestions, we need to create the suggestionbox
            const target = firstEmptyKeyword();
            let myKw;
            let id;
            for (const kw of input.keywords) {
                if (kw.keyword.oldId) {
                    myKw = kw
                    break;
                }
            }
            if (myKw) {
                id = target.el.id = `kw-${myKw.keyword.id}`;
                target.el.setAttribute("name", target.el.id);

                // Change button values
                let btn = target.el.nextSibling
                while (btn) {
                    if (btn.tagName === "BUTTON") {
                        btn.value = id;
                    }
                    btn = btn.nextSibling;
                }
                target.el.parentNode.id = id.replace("kw-", "kww-");
            } else {
                id = target.el.id
            }

            document.getElementById("btn_generatePoem").setAttribute("disabled", true);
            const SB = new Suggestionbox({
                selector: Keyword.formatID({id: parseInt(id.split("-")[1]), prefix: "suggB-kw-"}),
                id: Keyword.formatID({id: parseInt(id.split("-")[1]), prefix: "suggB-kw-"}),
                refresher_value: keywordBox.n,
                verse: Keyword,
                location: keywordBox.list,
                suggestions: input.keywordSuggestions.suggestions
            });

            let f5Btn
            if (input.keywordSuggestions.suggestions[0].suggestion.text.split(",").length === 1) {
                f5Btn = document.querySelector('[id^="btn-f5-lst-sug"]');
                if (f5Btn) {
                    f5Btn.name = f5Btn.id = f5Btn.name.replace("-sug-", "-1sug-");
                    f5Btn.value = 1
                }
            } else {
                f5Btn = document.querySelector('[id^="btn-f5-lst-1sug"]');
                if (f5Btn) {
                    f5Btn.name = f5Btn.id = f5Btn.name.replace("-sug-", "-sug-");
                    f5Btn.value = 4
                }
            }
            activateSuggestionbox();
        }
        if (input.keywords && input.keywords.length > 0) {
            keywordBox.header.disable()
            keywordBox.header.enable({includeGenButton: false})
        }

        const firstWr = keywordList.firstChild;
        let Wr;
        let previousWr;
        input.keywords.forEach(kw => {
            // after a save, some keywords will have an oldId, search the elements by oldId and rename
            if (kw.keyword.oldId) {
                const myFld = Keyword.getWrapper(document.getElementById(kw.oldId));
                if (myFld) {
                    let id = target.el.id = "kw-" + input.keywords[0].keyword.id;
                    target.el.setAttribute("name", target.el.id);
                    // Change button values
                    let btn = target.el.nextSibling
                    while (btn) {
                        if (btn.tagName === "BUTTON") {
                            btn.value = id;
                        }
                        btn = btn.nextSibling;
                    }
                    target.el.parentNode.id = id.replace("kw-", "kww-");
                }
            } else if (!input.keywordSuggestions) {
                // There is no oldId, we are rendering a poem from the database and create objects for each keyword
                // But only when there is no suggestionbox to render
                const id = kw.keyword.id;
                if (firstWr && !previousWr) {
                    Wr = firstWr
                    Wr.id = "kww-" + id;
                    Wr.firstChild.value = kw.keyword.text;
                    Wr.firstChild.id = Wr.firstChild.name = "kw-" + id;
                } else {
                    Wr = keywordList.addKeywordWrapper({
                        selector: "kww-" + id,
                        id: "kww-" + id,
                        value: kw.keyword.text,
                        buttons: previousWr.buttons,
                        events: previousWr.events
                    });
                }
                for (const btn of Wr.el.children) {
                    if (btn.id.startsWith("btn_del")) {
                        btn.value = "kw-" + id
                        btn.style.display = "inline-block";
                        btn.disabled = false;
                    } else if (btn.id.startsWith("btn_random")) {
                        btn.value = "kw-" + id;
                        btn.style.display = "none";
                    }
                }
                previousWr = Wr
            }
        })
    } else if (input.kwAccept) {
        if (input.kwAccept.nmfDim && input.kwAccept.nmfDim > 0) {
            document.getElementById("nmfDim").value = input.kwAccept.nmfDim;
        }

        let target = undefined;
        let Wr = undefined;
        let previous = 0;
        let previousWr = null;
        for (const [id, text] of Object.entries(input.kwAccept.keywords)) {
            if (target == undefined) {
                target = document.getElementById("kw-" + id);
                target.value = text;
                Wr = Keyword.getWrapper(target).parent;
            } else {
                Wr = keywordList.addKeywordWrapper({
                    selector: "kww-" + id,
                    id: "kww-" + id,
                    value: text,
                    buttons: previousWr.buttons,
                    events: previousWr.events
                });
            }
            previous = id;
            previousWr = Wr;

            for (const btn of Wr.el.children) {
                if (btn.id.startsWith("btn_del")) {
                    btn.value = "kw-" + id
                    btn.style.display = "inline-block";
                    btn.disabled = false;
                } else if (btn.id.startsWith("btn_random")) {
                    btn.value = "kw-" + id;
                    btn.style.display = "none";
                }
            }
            activateKeywordbox({})
        }
    }
    // @ every round trip, stanzas, verses, ... are updated -> retrieve the new id's
    if (input.stanzas) {
        const SB = document.getElementById("struct-sandbox");
        for (const s of input.stanzas) {
            if (s.stanza.oldId) {
                const stanza = document.getElementById(s.stanza.oldId);
                if (stanza) {
                    stanza.id = "s-" + s.stanza.id;
                    SB.value = SB.value.replace(s.stanza.oldId, "s-" + s.stanza.id);
                    const S = document.getElementById("struct-" + s.stanza.oldId);
                    S.id = "struct-s-" + s.stanza.id;
                    S.setAttribute("name", S.id);
                    if (s.stanza.verses) {
                        for (const vw of s.stanza.verses) {
                            if (vw.verse.oldId) {
                                const verseWrapper = document.getElementById(vw.verse.oldId.replace("v-", "vw-"));
                                if (verseWrapper) {
                                    verseWrapper.id = "vw-" + vw.verse.id;
                                    S.value = S.value.replace(vw.verse.oldId.replace("v-", "vw-"), "vw-" + vw.verse.id);
                                    const VW = document.getElementById("struct-" + vw.verse.oldId.replace("v-", "vw-"));
                                    VW.id = "struct-vw-" + vw.verse.id;
                                    VW.setAttribute("name", VW.id);
                                    const verse = document.getElementById(vw.verse.oldId);
                                    if (verse) {
                                        verse.id = "v-" + vw.verse.id;
                                        verse.setAttribute("name", verse.id)
                                        VW.value = VW.value.replace(vw.verse.oldId, "v-" + vw.verse.id);
                                        const V = document.getElementById("struct-" + vw.verse.oldId)
                                        V.setAttribute("name", "struct-v-" + vw.verse.id);
                                        V.id = V.name
                                        let btn = verseWrapper.firstChild;
                                        while (btn) {
                                            if (btn.tagName === "BUTTON") {
                                                btn.value = verse.id;
                                            }
                                            btn = btn.nextSibling;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

export function deleteKeyword(keyword) {
    const keywordBox = getKeywordbox();
    const keywordList = keywordBox.list;
    const deletedWrapper = KeywordWrapper.getWrapper(document.getElementById("kww-" + keyword.deleted));
    const deletedKeywordEL = deletedWrapper.firstChild.el;
    let id;

    // Look for the first empty keyword
    const kwFields = document.querySelectorAll('input[id^="kw-"]');
    const emptyKwFields = Array.from(kwFields).filter(el => el.value.trim() === "");
    if (emptyKwFields.length > 0 && !(emptyKwFields.length === 1 && emptyKwFields[0].id === deletedKeywordEL.id)) {
        emptyKwFields[0].focus();
    } else { // If no empty keyword field is found, we can create a new field
        const Wr = keywordList.addKeywordWrapper({
            selector: id ? "kww-" + id : null,
            id: id ? "kww-" + id : null,
            value: "",
            buttons: deletedWrapper.buttons,
            events: deletedWrapper.events
        });
        for (const btn of Wr.el.children) {
            if (btn.id.startsWith("btn_del")) {
                btn.value = Wr.id.replace("kww-", "kw-");
                btn.style.display = "none";
                btn.disabled = false;
            } else if (btn.id.startsWith("btn_random")) {
                btn.value = Wr.id.replace("kww-", "kw-");
                btn.style.display = "inline-block";
            }
        }
        Wr.firstChild.el.focus()
    }
    deletedWrapper.remove()
    activateKeywordbox();
    if (document.querySelectorAll('input[id^="kw-"]').length === 1) {
        keywordBox.header.enable();
    }
}

export function firstEmptyKeyword() {
    const keywordList = getKeywordbox().list;
    for (let kww of keywordList.children) {
        let kw = kww.firstChild;
        if (kw.value === "") {
            return kw;
        }
    }
}

export function updateNmfDim(nmfDim) {
    const nmfFld = document.getElementById("nmfDim");
    nmfFld.value = nmfDim;
}

export function updatePoemId(poemId) {
    const myFld = document.getElementById("poem_id");
    myFld.value = poemId;
}

export function updateElementIds(keywordsSaved) {
    const keywords = keywordsSaved.keywords;
    keywords.forEach(kw => {
        if (kw.keyword.oldId) {
            const domEl = document.getElementById(kw.keyword.oldId)
            domEl.id = domEl.name = "kw-" + kw.keyword.id;
            domEl.parentNode.id = "kww-" + kw.keyword.id;
            // Look if there is a button next to the element
            let btn = domEl.nextElementSibling;
            while (btn) {
                if (btn && btn.tagName === "BUTTON") {
                    btn.value = "kw-" + kw.keyword.id;
                }
                btn = btn.nextElementSibling;
            }
        }
    })
    const toRename = keywordsSaved.toRename;
    toRename.forEach(el => {
        const oldId = Object.keys(el)[0];
        if (oldId) {
            const id = el[oldId]
            const domEl = document.getElementById(oldId);
            domEl.id = id;
            // Look if there is a button next to the element
            const btn = domEl.nextElementSibling;
            if (btn && btn.tagName === "BUTTON") {
                btn.value = id;
            }
        }
    })
    // Update the structure elements
    if (toRename && toRename.length > 0) {
        const structRoot = document.getElementById("struct-sandbox");
        const structStanzas = structRoot.value.split(",");
        structStanzas.forEach(s => {
                const stNewId = toRename.find(st => st.hasOwnProperty(s))[s];
                if (stNewId) {
                    const stStructFld = document.getElementById("struct-" + s);
                    const structVerseWrappers = document.getElementById("struct-" + s).value.split(",");
                    structVerseWrappers.forEach(vw => {
                        const vwNewId = toRename.find(vrsW => vrsW.hasOwnProperty(vw))[vw];
                        const vwStructFld = document.getElementById("struct-" + vw);
                        if (vwNewId) {
                            const vStructFld = document.getElementById("struct-" + vw);
                            const structVerses = document.getElementById(vwStructFld.id).value.split(",");
                            structVerses.forEach(v => {
                                const vNewId = toRename.find(vrs => vrs.hasOwnProperty(v))[v];
                                const verseFld = document.getElementById("struct-" + v);
                                if (vNewId) {
                                    verseFld.id = verseFld.name = "struct-" + vNewId;
                                    vwStructFld.value = vwStructFld.value.replace(v, vNewId);
                                }
                                vStructFld.id = vStructFld.name = "struct-" + vNewId;
                                vwStructFld.value = vwStructFld.value.replace(vw, vwNewId);
                            })
                            vwStructFld.id = vwStructFld.name = "struct-" + vwNewId;
                            stStructFld.value = stStructFld.value.replace(vw, vwNewId);
                        }
                    })
                    stStructFld.id = stStructFld.name = "struct-" + stNewId;
                    structRoot.value = structRoot.value.replace(s, stNewId);
                }
            }
        )
    }
    document.getElementById("lang").value = keywordsSaved.lang;
}