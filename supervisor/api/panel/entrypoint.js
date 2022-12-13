
function loadES5() {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.7560e2e7.js';
  document.body.appendChild(el);
}
if (/.*Version\/(?:11|12)(?:\.\d+)*.*Safari\//.test(navigator.userAgent)) {
    loadES5();
} else {
  try {
    new Function("import('/api/hassio/app/frontend_latest/entrypoint.416f305d.js')")();
  } catch (err) {
    loadES5();
  }
}
  