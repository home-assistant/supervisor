
function loadES5() {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.5d40ff8b.js';
  document.body.appendChild(el);
}
if (/.*Version\/(?:11|12)(?:\.\d+)*.*Safari\//.test(navigator.userAgent)) {
    loadES5();
} else {
  try {
    new Function("import('/api/hassio/app/frontend_latest/entrypoint.f09e9f8e.js')")();
  } catch (err) {
    loadES5();
  }
}
  