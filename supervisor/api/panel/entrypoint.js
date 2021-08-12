
function loadES5() {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.ef32933f.js';
  document.body.appendChild(el);
}
if (/.*Version\/(?:11|12)(?:\.\d+)*.*Safari\//.test(navigator.userAgent)) {
    loadES5();
} else {
  try {
    new Function("import('/api/hassio/app/frontend_latest/entrypoint.7ca7c83a.js')")();
  } catch (err) {
    loadES5();
  }
}
  