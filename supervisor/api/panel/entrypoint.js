
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.5c3eb78c.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.9603bcfc.js';
  document.body.appendChild(el);
}
  