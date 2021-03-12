
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.d6c7a0d5.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.969fb073.js';
  document.body.appendChild(el);
}
  