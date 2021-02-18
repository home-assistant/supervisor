
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.17d3e180.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.1e6aec4d.js';
  document.body.appendChild(el);
}
  