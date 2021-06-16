
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.0d3c68f7.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.9e377d5a.js';
  document.body.appendChild(el);
}
  