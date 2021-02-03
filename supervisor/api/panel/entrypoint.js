
try {
  new Function("import('/api/hassio/app/frontend_latest/entrypoint.249906fa.js')")();
} catch (err) {
  var el = document.createElement('script');
  el.src = '/api/hassio/app/frontend_es5/entrypoint.9d919a57.js';
  document.body.appendChild(el);
}
  