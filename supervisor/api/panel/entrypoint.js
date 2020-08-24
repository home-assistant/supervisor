
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.68997ae5.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.f0a421ac.js';
  document.body.appendChild(el);
}
  