
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.7c5282d9.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.a6b5f4d5.js';
  document.body.appendChild(el);
}
  