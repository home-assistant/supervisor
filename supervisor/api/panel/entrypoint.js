
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.49151d80.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.a7c72a93.js';
  document.body.appendChild(el);
}
  