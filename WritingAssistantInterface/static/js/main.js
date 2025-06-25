import {sandboxClick, verseKeydown, highlightIfEmpty} from "./sandboxInteraction.js";
import {Poem} from "./sandboxAPI/1_Poem.js";

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
        })
})
;

/**
 * Example of a poem object with only the rhyme scheme:
 * {
 *   "poem":{
 *     "rhymeScheme":{
 *       "name":"sonnet",
 *       "elements":[
 *         {
 *           "line":{
 *             "id":"1",
 *             "txt":"a"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"2",
 *             "txt":"b"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"3",
 *             "txt":"b"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"4",
 *             "txt":"a"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"5",
 *             "txt":""
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"6",
 *             "txt":"c"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"7",
 *             "txt":"d"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"8",
 *             "txt":"d"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"9",
 *             "txt":"c"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"10",
 *             "txt":""
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"11",
 *             "txt":"e"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"12",
 *             "txt":"f"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"13",
 *             "txt":"e"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"14",
 *             "txt":""
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"15",
 *             "txt":"f"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"16",
 *             "txt":"e"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"17",
 *             "txt":"f"
 *           }
 *         }
 *       ]
 *     }
 *   }
 * }
 */

