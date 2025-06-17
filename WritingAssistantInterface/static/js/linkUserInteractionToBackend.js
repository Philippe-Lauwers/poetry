import {receivePoem} from './interactionInSandbox.js';

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
      const gen = await fetch('/generate', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(data)
      });
      const json = await gen.json();

      // 3) Display
      document.getElementById('sandbox').textContent =
        json.poem ? receivePoem(json.poem) : 'Error';
    });

