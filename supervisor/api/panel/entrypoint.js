
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.f7e7035c.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.c862ef13.js';
  document.body.appendChild(el);
}
  