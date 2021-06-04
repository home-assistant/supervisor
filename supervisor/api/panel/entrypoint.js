
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.586ea840.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.8daaaeda.js';
  document.body.appendChild(el);
}
  