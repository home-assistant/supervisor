
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.26c6755b.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.6eae0885.js';
  document.body.appendChild(el);
}
  