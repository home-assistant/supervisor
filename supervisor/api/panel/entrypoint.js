
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.afd8dd1f.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.83a2047d.js';
  document.body.appendChild(el);
}
  