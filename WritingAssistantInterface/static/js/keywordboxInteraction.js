import {Keywordbox} from "./keywordboxAPI/1_Keywordbox.js";
import {BaseNode} from "./API.js";

/**
 * Read-only accessor for any code that merely needs to *use*
 * the existing poem.  Will be `null` until initSandbox() runs.
 */
export const getKeywordbox = () => Keywordbox.instance;

export function deactivateKeywordbox () {
    const keywordbox = getKeywordbox();
    console.log(keywordbox);
    console.log(keywordbox.header);
    console.log(keywordbox.list);
    keywordbox.header.disable();
    keywordbox.list.disable();
}