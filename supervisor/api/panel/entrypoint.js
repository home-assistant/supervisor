
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.b213c589.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.4d2b84de.js';
  document.body.appendChild(el);
}
  