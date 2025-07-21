import {receivePoem} from './sandboxInteraction.js';
import {getParambox, mockEnableSelect, receiveRhymeScheme} from './paramboxInteraction.js'
import {closeSuggestionBox} from "./suggestionboxInteraction.js";
import {receiveKeywords} from "./keywordboxInteraction.js";

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
        } else if (s_id === "btn_generateVerse" || s_id.startsWith("btn-f5-lst-sug-v")) {
            reqRoute = "/generateVerse";
        } else if (s_id.startsWith("btn_acceptSuggestion")) {
            reqRoute = "/acceptSuggestion";
        } else if (s_id === "btn_savePoem") {
            reqRoute = "/savePoem";
        } else if (s_id === "btn_editPoem") {
            reqRoute = "/savePoem";
        } else if (s_id === "btn_randomKeywords" || s_id.startsWith("btn-f5-lst-sug-kw")) {
            reqRoute = "/randomKeywords";
        } else if (s_id === "btn_random1Keyword") {
            reqRoute = "/randomKeywords";
        }
        // 2) Route request
        let gen = await fetch(reqRoute, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const json = await gen.json();
console.log("Response from server: ", json);
        // 3) Display
    json.poem ? receivePoem(json.poem) : json.suggAccept ? closeSuggestionBox({
        YesOrNo: json.suggAccept,
        verse_id: json.verse_id
    }) : json.keywords ? receiveKeywords(json.keywords) : json.kwAccept ? closeSuggestionBox({
        YesOrNo: json.kwAccept, keyword_id: keyword_id
    }) : null;
        document.getElementById("btn_savePoem").removeAttribute("disabled");
        console.log("before mockEnableSelect");
        mockEnableSelect("form")
        console.log("after mockEnableSelect");
        if (reqRoute==="/savePoem" || reqRoute==="/editPoem") getParambox().getFinal().addEdit()
        console.log("Form submitted and processed successfully.");
    });

const formFld = document.getElementById('form');
formFld.addEventListener('change', async e => {
    const rhymeScheme = receiveRhymeScheme();
    console.log("Rhyme scheme updated to " , rhymeScheme);
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