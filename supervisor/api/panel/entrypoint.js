
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.4050b348.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.bcf8e8ff.js';
  document.body.appendChild(el);
}
  