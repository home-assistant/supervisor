
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.e56422ed.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.2bcfb839.js';
  document.body.appendChild(el);
}
  