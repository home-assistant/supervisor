
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.bb2cab5a.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.71a38014.js';
  document.body.appendChild(el);
}
  