
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.cf81f6d9.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.c258a457.js';
  document.body.appendChild(el);
}
  