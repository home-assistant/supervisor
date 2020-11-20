
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.4ec3f364.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.1799405f.js';
  document.body.appendChild(el);
}
  