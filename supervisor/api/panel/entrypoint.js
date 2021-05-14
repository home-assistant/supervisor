
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.fa10cbe0.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.338eaf3e.js';
  document.body.appendChild(el);
}
  