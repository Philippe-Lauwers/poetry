import {receivePoem} from './sandboxInteraction.js';
import {activateParambox, getParambox, mockEnableSelect, receiveRhymeScheme} from './paramboxInteraction.js'
import {closeSuggestionBox} from "./suggestionboxInteraction.js";
import {activateKeywordbox, deleteKeyword, receiveKeywords, updateNmfDim} from "./keywordboxInteraction.js";
import {handleLogin} from "./loginInteraction.js";

const form = document.getElementById('poemForm');
form.addEventListener('submit', async e => {
    e.preventDefault();

    // grab data from the form
    const frmData = new FormData(form);
    frmData.append(e.submitter.name, e.submitter.value);
    const data = Object.fromEntries(frmData.entries());


    let reqRoute = ""
    const s_id = e.submitter.id
    if (s_id === "btn_login") {
        reqRoute = "/login";
    } else if (s_id === "btn_generatePoem") {
        reqRoute = "/generatePoem";
    } else if (s_id === "btn_generateVerse" || s_id.startsWith("btn-f5-lst-sug-v")) {
        reqRoute = "/generateVerse";
    } else if (s_id.startsWith("btn_acceptSuggestion_v")) {
        reqRoute = "/acceptSuggestion";
    } else if (s_id === "btn_savePoem") {
        reqRoute = "/savePoem";
    } else if (s_id === "btn_editPoem") {
        reqRoute = "/savePoem";
    } else if (s_id === "btn_randomKeywords" || s_id.startsWith("btn-f5-lst-sug-kw")) {
        reqRoute = "/randomKeywords";
    } else if (s_id === "btn_random1Keyword" || s_id.startsWith("btn-f5-lst-1sug-kw")) {
        reqRoute = "/randomKeywords";
    } else if (s_id.startsWith("btn_acceptSuggestion_kw")) {
        reqRoute = "/acceptKeywordSuggestion";
    } else if (s_id === "btn_saveKeywords") {
        reqRoute = "/saveKeywords";
    } else if (s_id === "btn_deleteKeyword") {
        reqRoute = "/deleteKeyword";
    }
    // 2) Route request
    let gen = await fetch(reqRoute, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'include',
        body: JSON.stringify(data)
    });

    const json = await gen.json();
    // 3) Display
    if (json.login) {
        return handleLogin(json.login);
    } else if (json.poem) {
        receivePoem(json.poem);
        document.getElementById("nmfDim").value = json.poem.parameters.nmfDim;
    } else if (json.suggAccept) {
        closeSuggestionBox({verse: json});
        document.getElementById("nmfDim").value = json.suggAccept.nmfDim;
    } else if (json.keywords) {
        receiveKeywords(json.keywords);
    } else if (json.kwAccept) {
        closeSuggestionBox({keywords: json});
    } else if (json.keywordsSaved) {
        activateKeywordbox();
        activateParambox()
        updateNmfDim(json.keywordsSaved.nmfDim);
    } else if (json.kwDelete) {
        deleteKeyword(json.kwDelete);
    }
    mockEnableSelect("form")
    if (reqRoute === "/savePoem" || reqRoute === "/editPoem") getParambox().getFinal().addEdit()
});

const formFld = document.getElementById('form');
if (formFld) {
    formFld.addEventListener('change', async e => {
        const rhymeScheme = receiveRhymeScheme();
    });
}

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