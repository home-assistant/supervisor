
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.cfec6eb5.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.9b944a05.js';
  document.body.appendChild(el);
}
  