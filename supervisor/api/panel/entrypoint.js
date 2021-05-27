
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.e529ad28.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.9696f64f.js';
  document.body.appendChild(el);
}
  