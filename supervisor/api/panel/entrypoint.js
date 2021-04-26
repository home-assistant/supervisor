
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.780b9fd2.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.c8691e19.js';
  document.body.appendChild(el);
}
  