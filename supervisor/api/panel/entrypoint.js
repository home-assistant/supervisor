
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.js';
  document.body.appendChild(el);
}
  