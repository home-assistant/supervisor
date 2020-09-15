
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.ced77c9a.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.871af696.js';
  document.body.appendChild(el);
}
  