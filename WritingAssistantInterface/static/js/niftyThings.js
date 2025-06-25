import {BaseNode} from './API.js';

/** FUNCTIONALITY TO MAKE THE INTERFACE MORE PLEASANT */


/**
 * Shows a transient message right above a .verse-wrapper.
 * @param {HTMLElement} wrapper  – the .verse-wrapper element
 * @param {string}      text     – message to display
 * @param {number}      ms       – how long before it fades out
 */
export function flashMessage(host, text, ms = 1750) {
    // Accept either a wrapper or a plain DOM element
    const el = host instanceof BaseNode ? host.el : host;

    const msg = document.createElement('div');
    msg.className = 'inline-msg';
    msg.textContent = text;
    el.insertBefore(msg, el.firstChild);

    // Let CSS run its fade-in
    requestAnimationFrame(() => msg.classList.add('show'));

    let done = false;          // flag to prevent double-dismiss
    function hide() {
        if (done) return;
        done = true;

        clearTimeout(auto);               // stop auto-timer
        el.removeEventListener('click', hide);
        window.removeEventListener('keydown', hide);

        // fade OUT
        msg.classList.remove('show');     // opacity → 0 (CSS handles transition)

        // remove when the transition ends – or as a fallback after 300 ms
        const rm = () => msg.remove();
        msg.addEventListener('transitionend', rm, {once: true});
        setTimeout(rm, 300);
    }

    // Start the clock to remove the message after `ms` milliseconds
    const auto = setTimeout(hide, ms)

    // places adding eventlisteners to field in the queue to allow bubbling up the event to the window-level
    setTimeout(() => {
        el.addEventListener('keydown', function onKey(e) {
            // only if focus is in one of our verse‐inputs
            if (el.contains(e.target) && e.target.tagName === 'INPUT') {
                // block tab/enter
                if (e.key === 'Tab' || e.key === 'Enter') {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                }
                hide();
                // tear down this listener immediately
                el.removeEventListener('keydown', onKey, true);
            }
        }, {capture: true});   // <-- capture: true is the magic
    }, 0);

    el.addEventListener('click', hide, {once: true});
};