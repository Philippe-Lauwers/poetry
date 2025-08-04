import {loadPoemList} from "./poemlistInteraction.js";

export function handleLogin(login) {
    if (login.status === true) {
        loadPoemList();
    } else {
        document.getElementById("loginError").innerText = login.message;
    }
}