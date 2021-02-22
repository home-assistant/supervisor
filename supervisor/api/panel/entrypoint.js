
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.d505d83a.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.6ce56a3d.js';
  document.body.appendChild(el);
}
  