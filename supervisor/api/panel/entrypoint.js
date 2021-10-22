
function loadES5() {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.ab1549ac.js';
  document.body.appendChild(el);
}
if (/.*Version\/(?:11|12)(?:\.\d+)*.*Safari\//.test(navigator.userAgent)) {
    loadES5();
} else {
  try {
    new Function("import('/api/hassio/app/frontend_latest/entrypoint.0225e84d.js')")();
  } catch (err) {
    loadES5();
  }
}
  