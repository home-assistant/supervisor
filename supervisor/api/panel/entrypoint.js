
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.f7e32a92.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.31c760ab.js';
  document.body.appendChild(el);
}
  