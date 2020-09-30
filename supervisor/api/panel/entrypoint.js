
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.db541070.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.aaeeb8e2.js';
  document.body.appendChild(el);
}
  