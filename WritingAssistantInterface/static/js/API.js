// base-node.js
export class BaseNode {
    static #registry = new WeakMap();

    /**
     * Constructor class: searches for element by id, creates a new one if needed
     * @param  {Object}  opts
     * @param  {string|HTMLElement} [opts.selector]  – CSS selector or existing element
     * @param  {string}  [opts.tag="div"]            – tag name to create if none found
     * @param  {string}  [opts.id]                   – id to apply if creating
     * @param  {string}  [opts.type]                 – type, applies only to input elements
     * @param  {string}  [opts.className]            – className to apply if creating
     * @param  {Object<string,Function>} [opts.events] – event listeners to attach
     * @param  {Object<string,Function>} [opts.buttons] – buttons to attach*/
    constructor({
                    selector = null,
                    tag = "div",
                    type = "",
                    id = "",
                    value = "",
                    className = "",
                    events = {},
                    buttons = {}
                } = {}) {
        let el;
        // 1) if the function was passed an HTMLElement, use the HTMLElement
        if (selector instanceof HTMLElement) {
            el = selector;
        }
        // 2) else if the function was passed a string, try to query it
        else if (typeof selector === "string") {
            el = document.querySelector(selector);
            if(!el) {
               el = document.getElementById(selector);
            }
        }
        // 3) if nothing was found, create a new DOM-element
        if (!el) {
            el = document.createElement(tag);
            if (id) el.id = id;
            if (type) el.type = type;
            if (className) el.className = className;
            if (value) el.value = value;
        }

        // 4) attach any given event listeners
        this._events = events;
        Object.entries(events).forEach(([ev, fn]) => {
            if (typeof fn === "function") el.addEventListener(ev, fn);
        });

        // 4) attach any given buttons
        this._buttons = buttons;
        Object.entries(buttons).forEach(([btn, fn]) => {
            if (typeof fn === "function") el.addButton({btn, fn});
        });

        // 5) store the (new) element and register for weak look-ups
        if (!(el instanceof HTMLElement)) {
            throw new TypeError("BaseNode expects an HTMLElement or valid selector");
        }
        this.el = el;
        BaseNode.#registry.set(el, this);
    }

    /**
     * Function to retrieve the BaseNode object linked to a DOM-element
     * @param domEl
     * @returns {any|null}
     */
    static getWrapper(domEl) {
        return BaseNode.#registry.get(domEl) || null;
    }

    /**
     * Append another BaseNode (or raw HTMLElement) and return the wrapper */
    append(child) {
        // Set node to child (if BaseNode) or corresponding BaseNode of the DOM-element
        const node = child instanceof BaseNode ? child : BaseNode.#registry.get(child);
        // Set childEl to the DOM-element of child or child if this is a BaseNode
        const childEl = node ? node.el : child;
        // Append the childEl to the DOM-element of the current object
        this.el.appendChild(childEl);
        return node ?? new BaseNode(childEl);     // fallback generic wrapper
    }

    remove() {
        console.log("removing", this);
        this.el.remove();
        BaseNode.#registry.delete(this.el);
    }


    /** === HANDLING BUTTONS === */
    /**
     * Method to add a button to the DOM-element that is linked to this object
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
    /**
     * The actual building of a button DOM-element
     * @param cfg   configuration of the buttons
     *   @param imgSrc     for image buttons
     *   @param alt = "",
     *   @param onClick = null,
     *   @param id
     *   */
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

    /** === HELPER METHODS/FUNCTIONS === */
    /**
     * Format the id of an element
     * @param id
     * @param prefix
     * @param suffix
     * @return formatted id
     */
    static formatID({id = null, prefix = "", suffix = ""}) {
        switch (typeof id) {
            case "string":
                return id.replace(/^#/, "");
            case "number":
                return prefix.concat(id, suffix);
            case "bigint":
                return prefix.concat(id, suffix);
            case null:
            default:
                return `xxx-${(Math.random() * 100).toString(36).substring(2, 12)}`;
        }
    }
    /**
     * Getter and setter for element id
     */
    get id() {
        return this.el.id;
    }
    set id(id) {
        this.el.id = id ?? "";
    }

    /**
     * Retrieve the events and the buttons of the object
     * @returns {{}}
     */
    get events(){
        return this._events;
    }
    get buttons() {
        return this._buttons;
    }

    /**
     * Basic functions to move through the object-tree
     */
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
    /**
     * @return BaseNode: the first child of a BaseNode instance, if it exists */
    get firstChild() {
        return BaseNode.#registry.get(this.el.firstElementChild) || null;
    }
    /**
     * @return BaseNode: the last child of a BaseNode instance, if it exists  */
    get lastChild() {
        return BaseNode.#registry.get(this.el.lastElementChild) || null;
    }
    /**
     * @returns BaseNode: the next sibling of a BaseNode instance, if it exists
     */
    get nextSibling() {
        return BaseNode.#registry.get(this.el.nextElementSibling) || null;
    }
    /**
     * @returns sibling||null: the previous sibling of a BaseNode instance, if it exists
     */
    get prevSibling() {
        return BaseNode.#registry.get(this.el.previousElementSibling) || null;
    }
}