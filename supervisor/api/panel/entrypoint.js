
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.c1a28650.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.54588d7a.js';
  document.body.appendChild(el);
}
  