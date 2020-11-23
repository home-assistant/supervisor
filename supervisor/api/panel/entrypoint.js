
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.048dda6f.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.683871b1.js';
  document.body.appendChild(el);
}
  