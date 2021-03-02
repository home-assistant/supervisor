
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.a5b7c2a9.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.3a11130b.js';
  document.body.appendChild(el);
}
  