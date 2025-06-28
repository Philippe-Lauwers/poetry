import {desactivateParambox} from "./paramboxInteraction.js";

export class Submit {

    static handler(e) {
        switch (e.submitter.id) {
            case "btn_generate":
                desactivateParambox(e, e.submitter);
        }
    }
}