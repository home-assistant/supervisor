
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.b954f17a.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.f1b08733.js';
  document.body.appendChild(el);
}
  