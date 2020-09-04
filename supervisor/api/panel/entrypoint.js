
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.e3f59ee9.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.6086a806.js';
  document.body.appendChild(el);
}
  