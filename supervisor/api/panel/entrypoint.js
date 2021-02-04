
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.b537a8c0.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.f493e22d.js';
  document.body.appendChild(el);
}
  