
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.babc4122.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.028a6bad.js';
  document.body.appendChild(el);
}
  