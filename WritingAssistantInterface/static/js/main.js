import {sandboxClick, verseKeydown, verseKeyup, highlightIfEmpty, getSandbox} from "./sandboxInteraction.js";
import {loadParambox, receiveRhymeScheme, getRhymeScheme} from "./paramboxInteraction.js";
import {Submit} from "./submitHandler.js";
import {Poem} from "./sandboxAPI/1_Poem.js";
import {Parambox} from "./paramboxAPI/1_Parambox.js";

window.addEventListener("DOMContentLoaded", () => {
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
                change: e => highlightIfEmpty(e, e.target)},
            buttons: {
                btn_generatePoem: {
                    id: "btn-gen-v-",
                    type: "submit",
                    formaction: "/generateVerse",
                    formmethod: "post",
                    className: "btn",
                    alt: "Request a new verse"
                }
            }
        });
    // add submit-handler
    document.getElementById("poemForm").addEventListener("submit", e => Submit.handler(e, e.target));
    if (v.el.isConnected) setTimeout(function () {v.el.focus();},100);
});
const parambox = new Parambox({
    selector: "#parambox",
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

loadParambox();
if (getRhymeScheme() == null) receiveRhymeScheme();