
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.5875b404.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.59ace4b4.js';
  document.body.appendChild(el);
}
  