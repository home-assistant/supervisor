
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.852b1a31.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.7526ecbb.js';
  document.body.appendChild(el);
}
  