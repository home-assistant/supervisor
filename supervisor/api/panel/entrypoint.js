
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.955fb63e.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.1f7fd266.js';
  document.body.appendChild(el);
}
  