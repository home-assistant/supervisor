
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.18a06d96.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.10e8b77d.js';
  document.body.appendChild(el);
}
  