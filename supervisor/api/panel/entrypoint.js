
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.00c1195f.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.1d118c6f.js';
  document.body.appendChild(el);
}
  