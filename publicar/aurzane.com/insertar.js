/* AURZANE · ajusta la altura de las calculadoras insertadas en otras webs (https://aurzane.com/insertar/) */
(function (w, d) {
  if (w.__azInsertar) return; w.__azInsertar = 1;
  w.addEventListener('message', function (e) {
    if (!/^https:\/\/([a-z]+\.)?aurzane\.com$/.test(e.origin) || !e.data || e.data.az !== 'alto') return;
    Array.prototype.forEach.call(d.querySelectorAll('iframe[data-aurzane]'), function (f) {
      if (f.contentWindow === e.source) f.style.height = Math.min(Math.max(+e.data.h || 0, 300), 4000) + 'px';
    });
  });
})(window, document);
