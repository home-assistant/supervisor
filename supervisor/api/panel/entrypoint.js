
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.ae0488d3.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.04b79aee.js';
  document.body.appendChild(el);
}
  