
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.fae75f85.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.358c173a.js';
  document.body.appendChild(el);
}
  