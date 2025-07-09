import {deactivateParambox} from "./paramboxInteraction.js";
import {disableGenBtn, getSandbox} from "./sandboxInteraction.js";

export class Submit {

    static handler(e) {
        if (e.submitter.id == "btn_generatePoem") {
            document.getElementById("lang").disabled = false;
            setTimeout(() => {
                deactivateParambox(e, e.submitter);
                disableGenBtn(e, {includeFld: true});
            }, 0);
        } else if (e.submitter.id.substring(0, e.submitter.id.lastIndexOf("-")) == "btn-gen-v") {
            setTimeout(() => {
                deactivateParambox(e, e.submitter);
                for (let el of e.submitter.parentNode.childNodes) {
                        el.disabled = true;
                  }
                e.submitter.disabled = true;
            }, 0);
        }
    }
}