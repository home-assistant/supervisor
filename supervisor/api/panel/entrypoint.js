
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.a14fe829.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.24698450.js';
  document.body.appendChild(el);
}
  