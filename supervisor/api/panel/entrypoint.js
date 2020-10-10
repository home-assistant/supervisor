
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.34e2ee3b.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.6573682b.js';
  document.body.appendChild(el);
}
  