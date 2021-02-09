
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.e0293e95.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.f68c0ea3.js';
  document.body.appendChild(el);
}
  