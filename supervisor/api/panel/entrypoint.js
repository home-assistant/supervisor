
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.6bc241a4.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.b71bd2af.js';
  document.body.appendChild(el);
}
  