import {initEditorInteractions} from "./editorInteraction.js";

export function initPoemListInteraction() {
    const list = document.getElementById("poem-list");
    if (!list) return;

    // "Create new poem" button
    const createBtn = document.getElementById("btn_createPoem");
    createBtn.addEventListener("click", (e) => {
        e.preventDefault();
        loadEditor(null);
    });
    const createLink = document.querySelector(".poem-creator-link");
    createLink.addEventListener("click", (e) => {
        e.preventDefault();
        loadEditor(null);
    });
    createLink.addEventListener("dblclick", (e) => {
        e.preventDefault();
        loadEditor(null);
    });

    document.querySelectorAll(".poem-entry").forEach((el) => {
        const poemKey = el.dataset.key;

        // Hover preview
        el.addEventListener("mouseenter", () => showPreview(el));
        el.addEventListener("mouseleave", scheduleClearPreview);

        // Delete button
        const deleteBtn = el.querySelector('[id^="btn_deletePoem"]');
        if (deleteBtn) {
            deleteBtn.addEventListener("click", deletePoem);
        }

        // Edit button
        const editBtn = el.querySelector('[id^="btn_editPoem"], [id^="btn_unlockPoem"]');
        if (editBtn) {
            editBtn.addEventListener("click", () => loadEditor(poemKey));
        }

        // Poem link click or double-click
        const link = el.querySelector(".poem-link");
        if (link) {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                loadEditor(poemKey);
            });
            link.addEventListener("dblclick", (e) => {
                e.preventDefault();
                loadEditor(poemKey);
            });
        }
    });
    // Add an event listener on all the buttons in this page
    document.querySelectorAll("button").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            disableList();
        });
    });

    preview = document.getElementById("poemPreview");
    let currentKey = null;
    let clearTimeoutId = null;

    initPoemPreview();
}

// Load the editor pane when the user clicks a poem entry (or the button next to it)
function loadEditor(poemKey) {
    fetch(`/loadEditPoem?key=${encodeURIComponent(poemKey)}`)
        .then(res => res.text())
        .then(html => {
            const container = document.querySelector(".bottom-pane");
            container.innerHTML = html;
            // Grabbing the poem-related data as found at the bottom of the editor subtemplate
            const scriptPoem = container.querySelector("#poem-data");
            const scriptRhyme = container.querySelector("#rhyme-data");

            let poemData = null;
            let rhymeData = null;

            try {
                if (scriptPoem) poemData = JSON.parse(scriptPoem.textContent);
                if (scriptRhyme) rhymeData = JSON.parse(scriptRhyme.textContent);
            } catch (err) {
                poemData = null;
                rhymeData = null;
            }
            // When the editor is loaded, initialize its interactions (eventListeners, etc.)
            initEditorInteractions({poem: poemData, rhymeData: rhymeData});
        });
}

// Variables needed for proper operation of the poem preview
let preview;
let currentKey = null;
let clearTimeoutId = null;

export function initPoemPreview() {
    /** HANDLING THE POEM PREVIEW */

    // Set up preview entry hover
    document.querySelectorAll(".poem-entry").forEach((el) => {
        el.addEventListener("mouseenter", () => {
            clearTimeout(clearTimeoutId);
            showPreview(el);
        });
        el.addEventListener("mouseleave", scheduleClearPreview);
    });

    // Keep preview on hover
    preview.addEventListener("mouseenter", () => {
        clearTimeout(clearTimeoutId);
    });
    preview.addEventListener("mouseleave", scheduleClearPreview);
}

function showPreview(entry) {
    const text = entry.dataset.text || "";
    const title = entry.dataset.title || "";
    const key = entry.dataset.key;

    if (currentKey === key) return;
    currentKey = key;

    preview.innerHTML =
        (title ? `<h1><pre>${escapeHtml(title)}</pre></h1>` : "") +
        (text ? `<pre>${escapeHtml(text)}</pre>` : "");

    preview.classList.add("show");
}

function scheduleClearPreview() {
    clearTimeoutId = setTimeout(() => {
        currentKey = null;
        preview.classList.remove("show");
        preview.innerHTML = "";
    }, 300); // Match your CSS fade-out duration
}

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/** DELETE THE POEM (i.e. set its status to 0)*/
async function deletePoem(event) {
    const button = event.target;
    const poemKey = button.id.replace("btn_deletePoem_", "");

    // Send a request to the backend to delete the poem
    try {
        const response = await fetch(`/deletePoem?key=${encodeURIComponent(poemKey)}`);
        const result = await response.json();

        if (result.deleted === poemKey) {
            const li = button.closest('li.poem-entry');
            if (li) li.remove();
            const preview = document.getElementById("poemPreview");
            if (preview) {
                setTimeout(() => {

                    preview.classList.remove("show");
                    preview.innerHTML = ""
                    enableList();
                }, 100);
            }
        } else {
            console.warn(`Unexpected response from delete:`, result);
        }
    } catch (error) {
        console.error(`Failed to delete poem with key ${poemKey}:`, error);
    }
}

function disableList() {
    const list = document.querySelectorAll("button",);
    if (list) {
        list.forEach((btn) => {
            btn.disabled = true;
        });
    }
}

function enableList() {
    const list = document.querySelectorAll("button");
    if (list) {
        list.forEach((btn) => {
            btn.disabled = false;
        });
    }
}

export async function loadPoemList() {
    // If any struct- fields linger (from a previously reviewed poem), remove them
    const form = document.getElementById("poemForm");
    if (form) {
        const structInputs = form.querySelectorAll('input[id^="struct-"]');
        if (structInputs.length > 0) {
            structInputs.forEach(input => input.remove());
        }
    }

    try {
        const res = await fetch('/listPoems', {
            method: 'POST',                 // ← explicitly POST
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',  // if you need to send a body
                'X-Requested-With': 'XMLHttpRequest'
            },
            // body: JSON.stringify({ /* whatever data you need */ })
        });

        if (!res.ok) throw new Error(res.statusText);
        const html = await res.text();
        document.querySelector('.bottom-pane').innerHTML = html;
        initPoemListInteraction();
    } catch (err) {
        console.error('Failed to load poems:', err);
    }
}
