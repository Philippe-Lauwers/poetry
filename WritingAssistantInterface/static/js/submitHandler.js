import {desactivateParambox} from "./paramboxInteraction.js";
import {disableGenBtn, getSandbox} from "./sandboxInteraction.js";

export class Submit {

    static handler(e) {
        if (e.submitter.id == "btn_generatePoem") {
            desactivateParambox(e, e.submitter);
            disableGenBtn(e)

        } else if (e.submitter.id.substring(0,e.submitter.id.lastIndexOf("-")) == "btn-gen-v") {
            e.submitter.disabled = true;
        }
    }
}