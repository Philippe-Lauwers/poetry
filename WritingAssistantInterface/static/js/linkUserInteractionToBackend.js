import {receivePoem} from './sandboxInteraction.js';
import {getParambox, receiveRhymeScheme} from './paramboxInteraction.js'
import {closeSuggestionBox} from "./suggestionboxInteraction.js";
import {Parambox} from "./paramboxAPI/1_Parambox.js";
import {FinalWrapper} from "./paramboxAPI/4_FinalWrapper.js";

const form = document.getElementById('poemForm');
form.addEventListener('submit', async e => {
        e.preventDefault();

        // grab data from the form
        const frmData = new FormData(form);
        frmData.append(e.submitter.name, e.submitter.value);
        const data = Object.fromEntries(frmData.entries());

        // 1) Log the submission on your frontend Python
        await fetch('/log', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        let reqRoute = ""
        const s_id = e.submitter.id
        if (s_id === "btn_generatePoem") {
            reqRoute = "/generatePoem";
        } else if (s_id === "btn_generateVerse" || s_id.startsWith("btn-f5-lst-sug")) {
            reqRoute = "/generateVerse";
        } else if (s_id.startsWith("btn_acceptSuggestion")) {
            reqRoute = "/acceptSuggestion";
        } else if (s_id === "btn_savePoem") {
            reqRoute = "/savePoem";
        } else if (s_id === "btn_editPoem") {
            reqRoute = "/savePoem";
        }
        // 2) Route request
        let gen = await fetch(reqRoute, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const json = await gen.json();

        // 3) Display
        json.poem ? receivePoem(json.poem) : json.suggAccept ? closeSuggestionBox({YesOrNo:json.suggAccept, verse_id:json.verse_id}) :'Error';
        document.getElementById("btn_savePoem").removeAttribute("disabled");
        if (reqRoute==="/savePoem" || reqRoute==="/editPoem") getParambox().getFinal().addEdit()
    });

const formFld = document.getElementById('form');
formFld.addEventListener('change', async e => {
    receiveRhymeScheme();
});

export async function retrieveRhymeScheme() {
    const langFld = document.getElementById('lang').value;
    const formFld = document.getElementById('form').value;
    const rs = await fetch(`/poemForm?`
        + `lang=${encodeURIComponent(langFld)}`
        + `&form=${encodeURIComponent(formFld)}`, {
        method: 'GET',
    });
    const json = await rs.json();

    return json.rhymeScheme ? json : null;
}