/** Initializing the poem list interaction script */
/** Add event listeners to the poem entries for preview functionality */
if (document.getElementById("poem-list")) {
    for (const el of document.querySelectorAll(".poem-entry")) {
        el.addEventListener("mouseenter", function () {
            showPreview(el);
        });
        el.addEventListener("mouseleave", clearPreview);
    }
}


/** HANDLING THE POEM PREVIEW */
const preview = document.getElementById("poemPreview");
let currentKey = null;  // To track which poem is being previewed
/** ... show the preview */
function showPreview(entry) {
    const text = entry.dataset.text || "";
    const title = entry.dataset.title || null;
    const key = entry.dataset.key;

    if (currentKey === key) return; // Skip if we're already previewing this one

    currentKey = key;

    // Set new content immediately
    preview.innerHTML =
        (title?"<h1><pre>"+title+"</pre></h1>":"") +
        (text? `<pre>${escapeHtml(text)}</pre>`: "");

    preview.classList.add("show");
}
/** ... clear the preview */
function clearPreview() {
    currentKey = null;
    preview.classList.remove("show")
    setTimeout(() => {
        if (!currentKey) preview.innerHTML = ""; // only clear if nothing new shown
    }, 300); // match your CSS transition duration
}

/** Helper function to escape HTML special characters in a string */
function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}