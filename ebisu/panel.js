// Botones del panel de Ebisu (pausar / reanudar). La cabecera X-Ebisu-Panel impide que otra pagina los pulse (CSRF).
document.querySelectorAll("button[data-accion]").forEach((b) => {
  b.addEventListener("click", async () => {
    const accion = b.dataset.accion;
    if (!confirm(accion === "pausa" ? "¿Pausar Ebisu? (en papel no tiene efecto)" : "¿Reanudar Ebisu?")) return;
    const r = await fetch("/control", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Ebisu-Panel": "1" },
      body: JSON.stringify({ accion }),
    });
    if (!r.ok) alert("No se pudo: " + (await r.text()));
    location.reload();
  });
});
