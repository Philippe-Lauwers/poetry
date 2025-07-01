import {receivePoem} from './sandboxInteraction.js';
import {receiveRhymeScheme} from './paramboxInteraction.js'

    const form = document.getElementById('poemForm');
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());

      // 1) Log the submission on your frontend Python
      await fetch('/log', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(data)
      });

      // 2) Request generation (proxied to backend)
      const gen = await fetch('/generatePoem', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(data)
      });
      const json = await gen.json();

      // 3) Display
      json.poem ? receivePoem(json.poem) : 'Error';
    });

    const formFld = document.getElementById('form');
    formFld.addEventListener('change', async e => {
        receiveRhymeScheme();
    });
    export async function retrieveRhymeScheme() {
        const langFld = document.getElementById('lang').value;
        const formFld = document.getElementById('form').value;
        const rs  = await fetch(`/poemForm?`
                                + `lang=${encodeURIComponent(langFld)}`
                                + `&form=${encodeURIComponent(formFld)}`, {
                                method: 'GET',
                                });
        const json =  await rs.json();

        return json.rhymeScheme ? json: null;
    }