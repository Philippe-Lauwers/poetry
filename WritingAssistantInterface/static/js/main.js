import{addField, handleFieldKeydown} from './interactionInSandbox.js';

// for now hard-coded, will be replaced by a more dynamic approach later
let _poemDesc = {"poem":{"rhymeScheme":{"name":"sonnet","elements":[{"line":{"id":"1","txt":"a"}},{"line":{"id":"2","txt":"b"}},{"line":{"id":"3","txt":"b"}},{"line":{"id":"4","txt":"a"}},{"line":{"id":"5","txt":""}},{"line":{"id":"6","txt":"c"}},{"line":{"id":"7","txt":"d"}},{"line":{"id":"8","txt":"d"}},{"line":{"id":"9","txt":"c"}},{"line":{"id":"10","txt":""}},{"line":{"id":"11","txt":"e"}},{"line":{"id":"12","txt":"f"}},{"line":{"id":"13","txt":"e"}},{"line":{"id":"14","txt":""}},{"line":{"id":"15","txt":"f"}},{"line":{"id":"16","txt":"e"}},{"line":{"id":"17","txt":"f"}}]}}}
// let _poemDesc = {"poem":{"rhymeScheme":{"name":"free verse","elements":[]}}}
export function getRhymeScheme() { return _poemDesc.poem.rhymeScheme; }
export function setRhymeScheme(s)  { _poemDesc.poem.rhymeScheme = s; }

window.addEventListener('DOMContentLoaded', () => {
  const sandbox = document.getElementById('sandbox');
  sandbox.addField({
    inputEvents: {
      keydown: e => handleFieldKeydown(e, e.target)
    }
  });
});

/**
 * Example of a poem object with only the rhyme scheme:
 * {
 *   "poem":{
 *     "rhymeScheme":{
 *       "name":"sonnet",
 *       "elements":[
 *         {
 *           "line":{
 *             "id":"1",
 *             "txt":"a"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"2",
 *             "txt":"b"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"3",
 *             "txt":"b"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"4",
 *             "txt":"a"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"5",
 *             "txt":""
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"6",
 *             "txt":"c"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"7",
 *             "txt":"d"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"8",
 *             "txt":"d"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"9",
 *             "txt":"c"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"10",
 *             "txt":""
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"11",
 *             "txt":"e"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"12",
 *             "txt":"f"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"13",
 *             "txt":"e"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"14",
 *             "txt":""
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"15",
 *             "txt":"f"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"16",
 *             "txt":"e"
 *           }
 *         },
 *         {
 *           "line":{
 *             "id":"17",
 *             "txt":"f"
 *           }
 *         }
 *       ]
 *     }
 *   }
 * }
 */

