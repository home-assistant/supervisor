
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.ff041f87.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.b5639dff.js';
  document.body.appendChild(el);
}
  