
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.855567b9.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.19035830.js';
  document.body.appendChild(el);
}
  