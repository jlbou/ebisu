// Panel de Ebisu: los graficos (Lightweight Charts, ebisu/vendor/) con los datos que la pagina lleva en JSON, y los
// botones (pausar / reanudar). La cabecera X-Ebisu-Panel impide que otra pagina pulse los botones (CSRF).
(() => {
  const datos = JSON.parse(document.getElementById("datos").textContent || "{}");
  const LWC = window.LightweightCharts;
  const COLOR = { ebisu: "#C9971F", ref: "#53625E", tinta: "#1F2A28", rojo: "#B5483B", rejilla: "#E6EEEB",
                  medias: { 20: "#A9D2C8", 50: "#6FB0A3", 100: "#2F786D", 200: "#C9971F" } };
  const euros = (v) => v.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
  const precio = (v) => v.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const porcentaje = (v) => v.toLocaleString("es-ES", { maximumFractionDigits: 1 }) + " %";

  function grafico(id, formato) {
    const el = document.getElementById(id);
    if (!el || !LWC) return null;
    return LWC.createChart(el, {
      autoSize: true,
      layout: { background: { type: "solid", color: "#FFFFFF" }, textColor: "#53625E", fontSize: 12,
                fontFamily: '"Atkinson Hyperlegible", system-ui, sans-serif' },
      grid: { vertLines: { visible: false }, horzLines: { color: COLOR.rejilla } },
      rightPriceScale: { borderVisible: false },
      timeScale: { borderVisible: false, fixLeftEdge: true, fixRightEdge: true },
      localization: { locale: "es-ES", priceFormatter: formato,
                      dateFormat: "dd/MM/yyyy" },
      crosshair: { mode: LWC.CrosshairMode.Magnet },
      handleScroll: { vertTouchDrag: false },
    });
  }

  function linea(chart, serie, opciones) {
    if (!chart || !serie || !serie.length) return;
    const s = chart.addSeries(LWC.LineSeries, Object.assign({ lineWidth: 2, priceLineVisible: false,
                                                               lastValueVisible: false }, opciones));
    s.setData(serie);
    return s;
  }

  const gv = grafico("g-valor", euros);
  linea(gv, datos.referencia, { color: COLOR.ref, lineStyle: LWC && LWC.LineStyle.Dashed, title: "Indexado" });
  linea(gv, datos.valor, { color: COLOR.ebisu, lineWidth: 3, lastValueVisible: true, title: "Ebisu" });
  gv && gv.timeScale().fitContent();

  const gc = grafico("g-caida", porcentaje);
  if (gc && datos.caida && datos.caida.length) {
    const a = gc.addSeries(LWC.AreaSeries, { lineColor: COLOR.rojo, topColor: "rgba(181,72,59,0.05)",
                                              bottomColor: "rgba(181,72,59,0.28)", lineWidth: 2,
                                              priceLineVisible: false, invertFilledArea: true });
    a.setData(datos.caida);
    gc.timeScale().fitContent();
  }

  for (const [pieza, d] of Object.entries(datos.piezas || {})) {
    const g = grafico("g-" + pieza, precio);
    if (!g) continue;
    for (const [m, serie] of Object.entries(d.medias)) linea(g, serie, { color: COLOR.medias[m], lineWidth: 2 });
    linea(g, d.precio, { color: COLOR.tinta, lineWidth: 2, lastValueVisible: true });
    g.timeScale().fitContent();
  }

  document.querySelectorAll("button[data-accion]").forEach((b) => {
    b.addEventListener("click", async () => {
      const accion = b.dataset.accion;
      if (!confirm(accion === "pausa" ? "¿Pausar Ebisu? En papel no tiene efecto." : "¿Reanudar Ebisu?")) return;
      const r = await fetch("/control", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Ebisu-Panel": "1" },
        body: JSON.stringify({ accion }),
      });
      if (!r.ok) alert("No se pudo: " + (await r.text()));
      location.reload();
    });
  });
})();
