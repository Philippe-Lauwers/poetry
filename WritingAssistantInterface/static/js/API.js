// base-node.js
export class BaseNode {
    static #registry = new WeakMap();
    static #poemElements = ["Poem","Stanza","VerseWrapper","Verse"];

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
                    name = null,
                    value = "",
                    htmlFor = "",
                    txt = "",
                    className = "",
                    addButtons = false,
                    // default values for events and buttons
                    events = {},
                    buttons = {}
                } = {}) {
        let isNew = false;
        let el;
        // 1) if the function was passed an HTMLElement, use the HTMLElement
        if (selector instanceof HTMLElement) {
            el = selector;
        }
        // 2) else if the function was passed a string, try to query it
        else if (typeof selector === "string") {
            el = document.querySelector(selector);
            if (!el) {
               el = document.getElementById(selector);
            }
        }
        // 3) if nothing was found, create a new DOM-element
        if (!el) {
            isNew = true;
            el = document.createElement(tag);
            if (type) el.type = type;
            if (id) el.id = id;
            el.setAttribute("name",name?name:["input","checkbox"].includes(tag)?id:type);
            if (type) el.type = type;
            if (className) el.className = className;
            if (htmlFor) el.setAttribute("for", htmlFor);
            if (value) el.value = value;
            if (txt) el.textContent = txt;
        }
        // 4) register the DOM-element
        this.el = el;
        BaseNode.#registry.set(el, this);

        // 5) attach any given event listeners
        this._events = events;
        Object.entries(events).forEach(([ev, fn]) => {
            if (typeof fn === "function") el.addEventListener(ev, fn);
        });

        // 6) attach any given buttons
        this._buttons = buttons;
        this._buttonMap = new Map();
        if (isNew || addButtons) {
            this._buttons = buttons;
            this._buttonMap = new Map();
            Object.entries(buttons).forEach(([key, val]) => {
                let cfg;
                if (typeof val === "function") {
                    cfg = {id: key, onClick: val};
                } else if (val && typeof val === "object") {
                    cfg = val
                }
                this.addButton(cfg)
            });
        }

        //7) store the (new) element and register for weak look-ups
        if (!(el instanceof HTMLElement)) {
            throw new TypeError("BaseNode expects an HTMLElement or valid selector");
        }

        //8) create a hidden input to send id's and structure back and forth

        if (BaseNode.#poemElements.includes(this.constructor.name)) {
            let fld;
            fld = document.createElement("input")
            fld.type = "hidden";
            fld.name = "struct-".concat(this.id);
            fld.id = fld.name;
            //document.getElementById("poemForm").appendChild(fld);
            document.getElementsByClassName("top-pane")[0].appendChild(fld);
        }
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
        // determine the child node (or create the new child node) the method will return
        const returnVal =  node ?? new BaseNode(childEl);     // fallback generic wrapper
        // Save the new element to the "struct-" field of the parent (for poem elements only)
        if (BaseNode.#poemElements.includes(this.constructor.name)) {
            const structFld = document.getElementById(`struct-${this.id}`)
            if (!structFld.value.includes(childEl.id))
            {
                structFld.value += (structFld.value ? "," : "") + childEl.id;
            }
        }
        return returnVal
    }

    /**
    * Insert another BaseNode (or raw HTMLElement) before a given and return the wrapper */
    insertBefore(child, beforeChild) {
        // Set node to child (if BaseNode) or corresponding BaseNode of the DOM-element
        const node = child instanceof BaseNode ? child : BaseNode.#registry.get(child);
        const beforeNode = beforeChild instanceof BaseNode ? beforeChild : BaseNode.#registry.get(beforeChild);
        // Set childEl to the DOM-element of child or child if this is a BaseNode
        const childEl = node ? node.el : child;
        const beforeChildEL = beforeNode ? beforeNode.el : beforeChild;
        // Append the childEl to the DOM-element of the current object
        this.el.insertBefore(childEl, beforeChildEL);
        // determine the child node (or create the new child node) the method will return
        const returnVal =  node ?? new BaseNode(childEl);     // fallback generic wrapper
        // Save the new element to the "struct-" field of the parent (for poem elements only)
        if (BaseNode.#poemElements.includes(this.constructor.name)) {
            const structFld = document.getElementById(`struct-${this.id}`)
                structFld.value += (structFld.value ? ",":"") + childEl.id;
        }
        return returnVal
    }


    remove() {
        this.children.forEach(child => {
            child.remove();
        })
        this.el.remove();
        BaseNode.#registry.delete(this.el);
    }

    deactivate() {
        this.children.forEach(child => {
            child.deactivate();
        });
        this.el.disabled = true;
        let btn = this.el.nextSibling??this.el.firstChild;
        while (btn) {
            if (btn instanceof HTMLButtonElement) {
                btn.disabled = true;
            }
            btn = btn.nextSibling;
        }
    }

    activate() {
        this.children.forEach(child => {
            child.activate();
        });
        this.el.disabled = false;
        let btn = this.el.nextSibling??this.el.firstChild;
        while (btn) {
            if (btn instanceof HTMLButtonElement) {
                btn.disabled = false;
            }
            btn = btn.nextSibling;
        }
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
        this._buttonMap.set(key, btn);

        this.el.appendChild(btn);
        return btn;
    }
    /**
     * Move a button from one parent to another.
     * @param btnOrId , the button to move, either as a DOM reference or by its id
     * @param oldParent
     * @param newParent
     */
    moveButton(btnOrId, oldParent, newParent) {
        const btn = btnOrId instanceof String?document.getElementById(btnOrId):btnOrId;
        let oldValue = btn.value
        let btnNum = btn.value.match(/\d+/);
        let newNum = newParent.id.match(/\d+/);
        btn.value = (btnNum && newNum)?btn.value.replace(String(btnNum[0]),String(newNum[0])):btn.value;
        btn.disabled = false;
        newParent.el.appendChild(btn);

        // Re-map the button
        // this._buttonMap.delete(oldId);
        this._buttonMap.set(btn.id, btn);
    }
    /**
     * Remove a button by (1) its id or (2) its DOM reference.
     * Returns true if something was removed.
     */
    removeButton(btnOrId) {
        const btn = this._buttonMap.get(btnOrId);
        if (!btn) return false;
        btn.remove();
        this._buttonMap.delete(btnOrId);
        return true;
    }
    /**
     * The actual building of a button DOM-element
     * @param cfg   configuration of the buttons
     *   @param alt = "",
     *   @param onClick = null,
     *   @param id
     *   @param value = "",
     * @return dom-element of type button
     *   */
    #buildButton(cfg) {
        const {
            alt = "",
            type = null,
            formaction = null,
            formmethod = null,
            onClick = null,
            id = null,
            name = null,
            value = null,
            className = null,
            disabled = false// optional stable id
        } = cfg;

        const btn = document.createElement("button");
        btn.type = type?type:"button";
        if (className) btn.classList.add(className);
        btn.id=id?id:"";
        btn.name=name?name:btn.id;
        btn.value=value?value:"";
        btn.disabled = disabled;

        if (typeof onClick === "function") {
            btn.addEventListener("click", onClick);
        }

        btn.title = alt ? alt : null;
        if (formmethod) {
            btn.formMethod = formmethod;
        }
        if(formaction) {
            btn.formAction = formaction;
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
     * Getter and setter for element name (to be used for buttons and inputs)
     */
    get name() {
        return this.el.getAttribute("name") ?? "";
    }
    set name(newName) {
        this.el.setAttribute("name",newName) ?? "";
    }

    /**
     *
     * @return {string}
     */
    get value() {
        return this.el.value ?? "";
    }
    set value(newValue) {
        this.el.value = newValue ?? "";
    }

    /**
     * Getter and setter for the className of the element
     */
    get className() {
        return this.el.className;
    }
    set className(className) {
        this.el.className = className ?? "";
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