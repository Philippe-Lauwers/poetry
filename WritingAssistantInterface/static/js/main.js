import {sandboxClick, verseKeydown, highlightIfEmpty} from "./sandboxInteraction.js";
import {loadParambox} from "./paramboxInteraction.js";
import {Submit} from "./submitHandler.js";
import {Poem} from "./sandboxAPI/1_Poem.js";
import {Parambox} from "./paramboxAPI/1_Parambox.js";

export function getRhymeScheme() {
    return _poemDesc.poem.rhymeScheme;
}

export function setRhymeScheme(s) {
    _poemDesc.poem.rhymeScheme = s;
}

// for now hard-coded, will be replaced by a more dynamic approach later
function readRhymeScheme(form) {
    switch (form) {
        case "sonnet":
            return {
                "poem": {
                    "rhymeScheme": {
                        "name": "sonnet",
                        "elements": [{"verse": {"id": "1", "txt": "a"}}, {
                            "verse": {
                                "id": "2",
                                "txt": "b"
                            }
                        }, {"verse": {"id": "3", "txt": "b"}}, {"verse": {"id": "4", "txt": "a"}}, {
                            "verse": {
                                "id": "5",
                                "txt": ""
                            }
                        }, {"verse": {"id": "6", "txt": "c"}}, {"verse": {"id": "7", "txt": "d"}}, {
                            "verse": {
                                "id": "8",
                                "txt": "d"
                            }
                        }, {"verse": {"id": "9", "txt": "c"}}, {
                            "verse": {
                                "id": "10",
                                "txt": ""
                            }
                        }, {"verse": {"id": "11", "txt": "e"}}, {
                            "verse": {
                                "id": "12",
                                "txt": "f"
                            }
                        }, {"verse": {"id": "13", "txt": "e"}}, {
                            "verse": {
                                "id": "14",
                                "txt": ""
                            }
                        }, {"verse": {"id": "15", "txt": "f"}}, {
                            "verse": {
                                "id": "16",
                                "txt": "e"
                            }
                        }, {"verse": {"id": "17", "txt": "f"}}]
                    }
                }
            }
            break;
        case "short":
            return {
                "poem": {
                    "rhymeScheme": {
                        "name": "short",
                        "elements": [{"verse": {"id": "1", "txt": "a"}}, {
                            "verse": {
                                "id": "2",
                                "txt": "b"
                            }
                        }, {"verse": {"id": "3", "txt": "b"}}, {"verse": {"id": "4", "txt": "a"}}, {
                            "verse": {
                                "id": "5",
                                "txt": ""
                            }
                        }, {"verse": {"id": "6", "txt": "c"}}, {"verse": {"id": "7", "txt": "d"}}, {
                            "verse": {
                                "id": "8",
                                "txt": "d"
                            }
                        }, {"verse": {"id": "9", "txt": "c"}}, {"verse": {"id": "10", "txt": ""}}]
                    }
                }
            }
            break;
        case "shorter":
            return {
                "poem": {
                    "rhymeScheme": {
                        "name": "shorter",
                        "elements": [{"verse": {"id": "1", "txt": "a"}}, {
                            "verse": {
                                "id": "2",
                                "txt": "b"
                            }
                        }, {"verse": {"id": "3", "txt": "b"}}, {"verse": {"id": "4", "txt": "a"}}]
                    }
                }
            }
            break;
        case "free verse":
            return {"poem": {"rhymeScheme": {"name": "free verse", "elements": []}}}
            break;
        default:
            break;
    }
}

let _poemDesc = readRhymeScheme("sonnet");

window.addEventListener("DOMContentLoaded", () => {
    const sandbox = new Poem({
        selector: "#sandbox",
        events: {                       // ← correct key
            click: e => sandboxClick(e)           // or e => sandboxClick(e)
        }
    });
    sandbox.addStanza()
        .addVerseWrapper()
        .addVerse({
            value: "",                        // initial text
            events: {
                keydown: e => verseKeydown(e, e.target),
                change: e => highlightIfEmpty(e, e.target)
            }
        });
    const parambox = new Parambox({selector: "#parambox"});
    loadParambox();

    // add submit-handler
    document.getElementById("poemForm").addEventListener("submit", e => Submit.handler(e, e.target));
});
