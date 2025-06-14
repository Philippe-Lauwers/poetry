/** FUNCTIONALITY TO MAKE THE INTERFACE MORE PLEASANT */


/**
 * Shows a transient message right above a .verse-wrapper.
 * @param {HTMLElement} wrapper  – the .verse-wrapper element
 * @param {string}      text     – message to display
 * @param {number}      ms       – how long before it fades out
 */
export function flashMessage(wrapper, text, ms = 1200) {
  const msg = document.createElement('div');
  msg.className = 'inline-msg';
  msg.textContent = text;

  wrapper.insertBefore(msg, wrapper.firstChild);
  requestAnimationFrame(() => (msg.style.opacity = '1'));

  setTimeout(() => {
    msg.style.opacity = '0';
    msg.addEventListener('transitionend', () => msg.remove(), { once: true });
  }, ms);
}
