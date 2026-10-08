// Carica Plotly dalla copia locale (site/vendor/, inserita dal workflow di Pages);
// se manca (es. server locale) ripiega sulla CDN jsDelivr del pacchetto npm.
window.plotlyReady = new Promise((resolve, reject) => {
  const sources = [
    "vendor/plotly.min.js",
    "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js",
  ];
  const tryNext = (i) => {
    if (i >= sources.length) return reject(new Error("Plotly non disponibile"));
    const s = document.createElement("script");
    s.src = sources[i];
    s.onload = () => (window.Plotly ? resolve(window.Plotly) : tryNext(i + 1));
    s.onerror = () => tryNext(i + 1);
    document.head.appendChild(s);
  };
  tryNext(0);
});
