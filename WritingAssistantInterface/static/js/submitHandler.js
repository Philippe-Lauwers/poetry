import {desactivateParambox} from "./paramboxInteraction.js";
import {getSandbox} from "./sandboxInteraction.js";

export class Submit {

    static handler(e) {
        switch (e.submitter.id) {
            case "btn_generate":
                desactivateParambox(e, e.submitter);
        }
    }
}