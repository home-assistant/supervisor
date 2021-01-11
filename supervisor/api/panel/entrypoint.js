
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.266bc30f.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.585f219b.js';
  document.body.appendChild(el);
}
  