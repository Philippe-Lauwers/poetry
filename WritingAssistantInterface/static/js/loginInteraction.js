import {initPoemListInteraction, loadPoemList} from "./poemlistInteraction.js";
import {flashMessage} from "./niftyThings.js";

export function handleLogin(login) {
    if (login.status === true) {
        loadPoemList();
    } else {
        document.getElementById("loginError").innerText = login.message;
    }
}

export function handleRegister(register) {
    const target = document.querySelector(".gdpr-consent-wrapper");
    if (register.status === true) {
        flashMessage(target, register.message ? register.message : "error",2000);
        setTimeout(() => {
            loadLogin();
        }, 2000);
    } else {
        const target = document.querySelector(".gdpr-consent-wrapper");
        flashMessage(target, register.message ? register.message : "error");
    }
}

export function initLoginInteraction() {
    document.getElementById("btn_register")?.addEventListener("click", loadRegister)
}

export function loadLogin() {
    fetch("/login")
        .then(res => {
            if (!res.ok) throw new Error("Failed to load login form");
            return res.text();
        })
        .then(html => {
            document.querySelector(".bottom-pane").innerHTML = html;
            initLoginInteraction();    // re-bind your login button handler
        })
        .catch(err => {
            console.error("Error loading login subtemplate:", err);
            flashMessage("Unable to load login form. Please try again.", "error");
        });
}

export function loadRegister() {
    fetch("/register")
        .then(res => res.text())
        .then(html => {
            document.querySelector(".bottom-pane").innerHTML = html;
            initRegisterInteraction();
        })
        .catch(err => {
            console.error("Failed to load register page:", err);
        });
}

export function initRegisterInteraction() {

}