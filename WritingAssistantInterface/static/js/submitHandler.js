import {desactivateParambox} from "./paramboxInteraction.js";
import {getSandbox} from "./sandboxInteraction.js";

export class Submit {

    static handler(e) {
        switch (e.submitter.id) {
            case "btn_generatePoem":
                desactivateParambox(e, e.submitter);
        }
    }
}