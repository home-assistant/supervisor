
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.4fa1b377.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.3608315c.js';
  document.body.appendChild(el);
}
  