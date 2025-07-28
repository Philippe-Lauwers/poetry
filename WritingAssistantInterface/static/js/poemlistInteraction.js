/** Initializing the poem list interaction script */
/** Add event listeners to the poem entries for preview functionality */
if (document.getElementById("poem-list")) {
    document.querySelectorAll(".poem-entry").forEach((el) => {
        el.addEventListener("mouseenter", function () {
            showPreview(el);
        });
        el.addEventListener("mouseleave", scheduleClearPreview);

    });
    /** Add event listener to the delete button on click */
    document.querySelectorAll('[id^="btn_deletePoem"]').forEach((button) => {
        button.addEventListener('click', deletePoem);
    });
}


/** HANDLING THE POEM PREVIEW */
const preview = document.getElementById("poemPreview");
let currentKey = null;
let clearTimeoutId = null;

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
                }, 0);
            }
        } else {
            console.warn(`Unexpected response from delete:`, result);
        }
    } catch (error) {
        console.error(`Failed to delete poem with key ${poemKey}:`, error);
    }
}