
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.639ed35e.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.054b9d8c.js';
  document.body.appendChild(el);
}
  