
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.e4508588.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.bed0b357.js';
  document.body.appendChild(el);
}
  