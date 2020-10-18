
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.cbedde60.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.96d2427f.js';
  document.body.appendChild(el);
}
  