import {
    getSandbox,
    highlightIfEmpty,
    receivePoem,
    sandboxClick,
    verseKeydown,
    verseKeyup
} from "./sandboxInteraction.js";
import {deactivateParambox, loadParambox, receiveRhymeScheme} from "./paramboxInteraction.js";
import {Submit} from "./submitHandler.js";
import {Poem} from "./sandboxAPI/1_Poem.js";
import {Parambox} from "./paramboxAPI/1_Parambox.js";
import {Keywordbox} from "./keywordboxAPI/1_Keywordbox.js";
import {FinalWrapper} from "./paramboxAPI/4_FinalWrapper.js";

export let rhymeSchemes;

export async function initEditorInteractions({poem = null, rhymeData = null} = {}) {
    const editor = document.getElementById("sandbox");
    if (!editor) return;
    rhymeSchemes = rhymeData
    // Initialize the editor
    const myParams = poem ? poem.parameters : null;
    await initializeEditor({poem: poem, parameters: myParams});
    if (poem) {
        receivePoem(poem)
    }
}

export async function initializeEditor({poem = null, parameters = null} = {}) {
    if (parameters) {
        document.getElementById("lang").value = parameters.lang;
        document.getElementById("form").value = parameters.form;
        document.getElementById("nmfDim").value = parameters.nmfDim;
    }
    if (document.getElementById("sandbox")) {
        const sandbox = new Poem({
            selector: "#sandbox",
            events: {                       // ← correct key
                click: e => sandboxClick(e)           // or e => sandboxClick(e)
            }
        });
        let v = sandbox.addStanza()
            .addVerse({
                value: "",// initial text
                events: {
                    keydown: e => verseKeydown(e, e.target),
                    keyup: e => verseKeyup(e, e.target),
                    change: e => highlightIfEmpty(e, e.target)
                },
                buttons: {
                    btn_generateVerse: {
                        id: "btn_generateVerse",
                        value: "v-1",
                        type: "submit",
                        formaction: "/generateVerse",
                        formmethod: "post",
                        className: "btn",
                        alt: "Request a new verse"
                    }
                }
            });
        // add submit-handler
        const form = document.getElementById("poemForm")
        form.addEventListener("submit", e => {
                document.getElementById("lang").disabled = false;
            },
            {capture: true}
        );
        form.addEventListener("submit", e => Submit.handler(e, e.target));
        if (v.el.isConnected) setTimeout(function () {
            v.el.focus();
        }, 0);
    }
    ;
    const parambox = new Parambox({
        selector: "#parambox",
        addButtons: true,
        buttons: {
            btn_generatePoem: {
                id: "btn_generatePoem",
                type: "submit",
                formaction: "/generatePoem",
                formmethod: "post",
                //imgSrc: "static/img/btn_GeneratePoem.svg",
                className: "btn",
                alt: "Generate a draft"
            }
        }
    });
    const keywordbox = new Keywordbox({selector: "#keywordbox"})

    // add event listeners to the parambox
    loadParambox();
    if (poem) {
        deactivateParambox()
    }
    // Set the status of the final checkbox (can only be done after the parambox is loaded)
    if (parameters) {
        const isFinal = document.querySelector(`input[name="chckBx_final"][value="${parameters.status}"]`)
        if (isFinal) {
            isFinal.checked = true;
            FinalWrapper.getWrapper(document.getElementById("final")).addEdit()
        }
    }
    await receiveRhymeScheme();
}

export function editorProtected({disable = None}) {
    // Input fields that should read-only (all except for the ones starting with "struct")
    const inputs = document.querySelectorAll(
        'input:not([id^="struct"]):not([name^="struct"])'
    );
    inputs.forEach(input => {
        input.readOnly = disable;
        if (input.type == "checkbox") {
            if (disable) {
                input.classList.add("read-only");
            } else {
                input.classList.remove("read-only");
            }
        }
    });
    // Buttons that should be disabled (all except for btn_editPoem)
    const firstFieldEmpty = getSandbox().firstChild.firstChild.firstChild.value === "";
    const buttons = document.querySelectorAll(
        'button' +
        ':not(#btn_editPoem):not([name="btn_editPoem"])' +
        ':not(#btn_goList):not([name="btn_goList"])');
    buttons.forEach(btn => {
        if ((btn.id !== "btn_generatePoem" || firstFieldEmpty) || disable) {
            // btn_generatePoem has to be disabled and [not enabled again if there is text in the first verse]
            btn.disabled = true;
        }
    });
}