
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.fa416948.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.732d3458.js';
  document.body.appendChild(el);
}
  