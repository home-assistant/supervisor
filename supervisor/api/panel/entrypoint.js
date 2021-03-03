
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.5b056535.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.6cdb4240.js';
  document.body.appendChild(el);
}
  