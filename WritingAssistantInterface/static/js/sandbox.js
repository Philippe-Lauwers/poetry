/* ============================================================================
 *  Tiny DOM-tree OO wrapper for a poem editor
 *  Classes: BaseNode → Poem → Stanza → VerseWrapper → Verse
 * ========================================================================== */
import {getRhymeScheme} from './main.js';

export class BaseNode {
    /** All node instances are stored here so that we can jump
     *  from a DOM element back to its JS wrapper in O(1). */
    static #registry = new WeakMap();

    constructor(el) {
        if (!(el instanceof HTMLElement)) {
            throw new TypeError("BaseNode expects an HTMLElement");
        }
        this.el = el;
        BaseNode.#registry.set(el, this);
    }

    static getWrapper(domEl) {
        return BaseNode.#registry.get(domEl) || null;
    }

    /* ---------- creation helpers (override in subclasses) ---------- */
    static createElement(tag, {id = "", className = ""} = {}) {
        const el = document.createElement(tag);
        if (id) el.id = id;
        if (className) el.className = className;
        return el;
    }

    /* ----------------------- tree traversal ----------------------- */
    /** Append another BaseNode (or raw HTMLElement) and return the wrapper */
    append(child) {
        const node = child instanceof BaseNode ? child : BaseNode.#registry.get(child);
        const childEl = node ? node.el : child;

        this.el.appendChild(childEl);
        return node ?? new BaseNode(childEl);     // fallback generic wrapper
    }

    get parent() {
        return BaseNode.#registry.get(this.el.parentElement) || null;
    }

    /**
     * @return children as an array of BaseNode instances */
    get children() {
        return Array.from(this.el.children)
            .map(el => BaseNode.#registry.get(el))
            .filter(Boolean);                 // remove nulls for un-registered nodes
    }

    get firstChild() {
        return BaseNode.#registry.get(this.el.firstElementChild) || null;
    }

    get lastChild() {
        return BaseNode.#registry.get(this.el.lastElementChild) || null;
    }

    get nextSibling() {
        return BaseNode.#registry.get(this.el.nextElementSibling) || null;
    }

    get prevSibling() {
        return BaseNode.#registry.get(this.el.previousElementSibling) || null;
    }
}

/* ============================================================================
 *  POEM  (root = #sandbox)
 * ========================================================================== */
export class Poem extends BaseNode {
    static #stanzaSeq = 0;

    /** Grab an existing poem container or create an empty one */
    static init(selector = '#sandbox', opts = {}) {
        /* ── 1.  allow "opts-object-only" call ─────────────────────────────── */
        if (typeof selector === 'object') {
            opts = selector;          // swap
            selector = '#sandbox';
        }

        /* ── 2.  legacy string shortcut (rarely used now) ──────────────────── */
        if (typeof opts === 'string') opts = {value: opts};

        /* ── 3.  pull out recognised options ───────────────────────────────── */
        const {
            events = {}                 // root-level listeners
        } = opts;

        /* ── 4.  get or create the root element ────────────────────────────── */
        const el =
            document.querySelector(selector) ??
            Poem.createElement('div', {id: selector.replace(/^#/, '')});

        /* ── 5.  attach listeners ──────────────────────────────────────────── */
        Object.entries(events).forEach(([ev, fn]) => {
            if (typeof fn === 'function') el.addEventListener(ev, fn);
        });

        /* ── 6.  build the Poem wrapper ────────────────────────────────────── */
        const poem = new Poem(el);

        return poem;
    }

    constructor(el) {
        super(el);
    }

    /** Convenience getter for whichever stanza holds a certain verse */
    findStanzaOf(verse) {
        let node = verse;
        while (node && !(node instanceof Stanza)) node = node.parent;
        return node;
    }

    countFields(poem) {
        let cnt = 0;
        for (let stanza of this.children) {
            cnt += stanza.countFields();
        }
        return cnt;
    }

    /** Convenience getter for the last stanza */
    lastStanza() {
        const last = this.lastChild;
        return last instanceof Stanza ? last : null;
    }

    /** Add a new stanza and return the Stanza wrapper */
    addStanza() {
        const id = `stanza-${++Poem.#stanzaSeq}`;
        const el = BaseNode.createElement("div", {id, className: "stanza-wrapper"});
        return this.append(new Stanza(el));
    }
}

/* ============================================================================
 *  STANZA
 * ========================================================================== */
export class Stanza extends BaseNode {
    static #verseWrapperSeq = 0;

    addVerseWrapper(buttons = []) {
        const id = `vw-${++Stanza.#verseWrapperSeq}`;
        const el = BaseNode.createElement("div", {id, className: "verse-wrapper"});
        const vw = new VerseWrapper(el, buttons);
        return this.append(vw);
    }

    /* --------------------------------------------------------------------------
 *  STANZA – enhanced addVerse()
 * ----------------------------------------------------------------------- */
    addVerse(opts = {}) {
        if (typeof opts === "string") opts = {value: opts};

        const {
            value = "",     // initial text inside the <input>
            buttons = [],     // [{ id, imgSrc, alt, onClick }, …]
            inputEvents = {}      // { eventName: handlerFn, … }
        } = opts;

        const vw = this.addVerseWrapper(buttons);   // <- buttons passed on to the wrapper
        const verse = vw.addVerse({value, inputEvents}); // <- events passed on to the verse input field
        return verse;
    }

    countFields() {
        return this.children.length;
    }
}

/* ============================================================================
 *  VERSE WRAPPER
 * ========================================================================== */

// ─── VERSE WRAPPER ─────────────────────────────────────────────────────────
export class VerseWrapper extends BaseNode {

    /**
     * @param {HTMLElement} el              – wrapper <div>
     * @param {Object}      opts            – { buttons: […] }
     */
    constructor(el, {buttons = []} = {}) {
        super(el);
        this.buttons = new Map();            // id → <button>
        buttons.forEach(cfg => this.addButton(cfg));
    }

    /* ══════════════════════  PUBLIC API  ═════════════════════ */

    /**
     * Add one button, return the created <button>.
     * @param {Object} cfg        – { id?, imgSrc, alt?, onClick? }
     */
    addButton(cfg) {
        const btn = this.#buildButton(cfg);

        // Track by id if supplied; otherwise by DOM reference
        const key = cfg.id ?? btn;
        this.buttons.set(key, btn);

        this.el.appendChild(btn);
        return btn;
    }

    /**
     * Remove a button by (1) its id or (2) its DOM reference.
     * Returns true if something was removed.
     */
    removeButton(btnOrId) {
        const key = this.buttons.has(btnOrId) ? btnOrId :         // id lookup
            [...this.buttons.entries()]
                .find(([, el]) => el === btnOrId)?.[0];     // ref lookup
        if (!key) return false;

        const btn = this.buttons.get(key);
        btn.remove();
        this.buttons.delete(key);
        return true;
    }

    /** Convenience passthrough to create a verse as before */
    addVerse(opts) {
        const verse = Verse.create(opts);
        return this.append(verse);
    }

    /* ═══════════════════  PRIVATE UTILITIES  ══════════════════ */

    #buildButton(cfg) {
        const {
            imgSrc,
            alt = "",
            onClick = null,
            id = null          // optional stable id
        } = cfg;

        const btn = document.createElement("button");
        btn.type = "button";
        btn.classList.add("field-btn");
        if (id) btn.dataset.id = id;

        const img = document.createElement("img");
        img.src = imgSrc;
        img.alt = alt;
        btn.appendChild(img);

        if (typeof onClick === "function") {
            btn.addEventListener("click", onClick);
        }
        return btn;
    }
}


/* ============================================================================
 *  VERSE (a single input[type=text])
 * ========================================================================== */
export class Verse extends BaseNode {
    static #seq = 0;

    static create(opts = "") {
        // Allow the old signature Verse.create("text")
        if (typeof opts === "string") opts = {value: opts};

        const {
            value = "",                 // initial input value
            inputEvents = {}            // { eventName: handlerFn, … }
        } = opts;

        // build the <input>
        const input = BaseNode.createElement("input", {
            id: `verse-${++Verse.#seq}`,
            className: "verse"
        });
        input.type = "text";
        input.value = value;

        // wire up event listeners
        Object.entries(inputEvents).forEach(([event, handler]) => {
            if (typeof handler === "function") input.addEventListener(event, handler);
        });
        return new Verse(input);
    }

    get value() {
        return this.el.value;
    }

    getValue() {
        return this.value;
    }

    set value(text) {
        this.el.value = text ?? "";
    }

    setValue(text = "") {
        this.value = text;
        return this;
    }
}