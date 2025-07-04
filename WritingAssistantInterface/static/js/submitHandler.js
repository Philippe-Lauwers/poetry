import {deactivateParambox} from "./paramboxInteraction.js";
import {disableGenBtn, getSandbox} from "./sandboxInteraction.js";

export class Submit {

    static handler(e) {
        if (e.submitter.id == "btn_generatePoem") {
            deactivateParambox(e, e.submitter);
            disableGenBtn(e, {includeFld: true});
        } else if (e.submitter.id.substring(0,e.submitter.id.lastIndexOf("-")) == "btn-gen-v") {
            e.submitter.disabled = true;
        }
    }
}