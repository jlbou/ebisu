"""El panel del bot en papel (decision 9; P5; docs/plan-bot-papel.md): una pagina tipo informe, generada sin
dependencias nuevas (HTML con los graficos en SVG). Se rehace al final de cada vuelta y al pulsar un boton.

Arriba, el resumen; debajo, por orden: 1) valor frente al indexado y las caidas; 2) cada pieza con sus 4 medias;
3) operaciones; 4) historial de la IA; 5) con y sin la IA (cada freno, en sombra: acerto si la pieza bajo);
6) Hacienda (en papel, simulada). En castellano y "la IA", nunca el nombre del modelo.
Colores de la marca: verde mar #1E5E57, oro #E3B341, crema #F3F1EA. Dos series: tambien por trazo y etiqueta.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from ebisu import estrategia as E
from ebisu import mensajes as m
from ebisu import papel as P
from ebisu import precios

RAIZ = Path(__file__).resolve().parents[1]
LOGO = RAIZ / "assets" / "logo" / "ebisu.svg"
VERDE, ORO, CREMA, TINTA, GRIS = "#1E5E57", "#E3B341", "#F3F1EA", "#1F2A28", "#6B7471"
RAMPA_MEDIAS = ("#9CC7BF", "#5E9F94", "#2F786D", "#123E39")  # 20, 50, 100, 200 dias: claro -> oscuro


def e(x: object) -> str:
    return html.escape(re.sub(r"(?i)claude", "la IA", str(x)))


def svg_lineas(series: list[tuple[str, pd.Series, str, str]], alto: int = 220, ancho: int = 760,
               formato=lambda v: f"{v:,.0f}") -> str:
    """Grafico de lineas en SVG. series = [(nombre, serie, color, trazo)]; etiqueta directa al final de cada una."""
    validas = [(n, s.dropna(), c, t) for n, s, c, t in series if len(s.dropna()) > 1]
    if not validas:
        return '<p class="vacio">Sin datos todavía.</p>'
    x0 = min(s.index[0] for _, s, _, _ in validas)
    x1 = max(s.index[-1] for _, s, _, _ in validas)
    vmin = min(float(s.min()) for _, s, _, _ in validas)
    vmax = max(float(s.max()) for _, s, _, _ in validas)
    if vmax == vmin:
        vmax = vmin + 1
    izq, der, arr, aba = 56, 110, 12, 26
    w, h = ancho - izq - der, alto - arr - aba
    total = max((x1 - x0).days, 1)

    def px(d):
        return izq + w * (d - x0).days / total

    def py(v):
        return arr + h * (1 - (v - vmin) / (vmax - vmin))

    partes = [f'<svg viewBox="0 0 {ancho} {alto}" role="img" class="grafico">']
    for k in range(5):  # rejilla y eje
        v = vmin + (vmax - vmin) * k / 4
        y = py(v)
        partes.append(f'<line x1="{izq}" x2="{izq + w}" y1="{y:.1f}" y2="{y:.1f}" class="rejilla"/>'
                      f'<text x="{izq - 6}" y="{y + 4:.1f}" class="eje" text-anchor="end">{e(formato(v))}</text>')
    for d in pd.date_range(x0, x1, periods=min(6, max(total // 30, 2))):
        partes.append(f'<text x="{px(d):.1f}" y="{alto - 6}" class="eje" text-anchor="middle">{d:%m/%y}</text>')
    for nombre, s, color, trazo in validas:
        puntos = " ".join(f"{px(d):.1f},{py(float(v)):.1f}" for d, v in s.items())
        guion = ' stroke-dasharray="6 4"' if trazo == "discontinuo" else ""
        partes.append(f'<polyline points="{puntos}" fill="none" stroke="{color}" stroke-width="2"{guion}>'
                      f'<title>{e(nombre)}</title></polyline>')
        ux, uy = px(s.index[-1]), py(float(s.iloc[-1]))
        partes.append(f'<circle cx="{ux:.1f}" cy="{uy:.1f}" r="4" fill="{color}" stroke="{CREMA}" stroke-width="2">'
                      f'<title>{e(nombre)}: {e(formato(float(s.iloc[-1])))} ({s.index[-1]:%d/%m/%Y})</title></circle>'
                      f'<text x="{ux + 8:.1f}" y="{uy + 4:.1f}" class="etiqueta">{e(nombre)}</text>')
    partes.append("</svg>")
    return "".join(partes)


def tarjeta(titulo: str, valor: str, nota: str = "") -> str:
    return f'<div class="tarjeta"><div class="t">{e(titulo)}</div><div class="v">{valor}</div><div class="n">{nota}</div></div>'


def puntos_html(n: int) -> str:
    return "".join('<span class="punto lleno"></span>' if i < n else '<span class="punto"></span>' for i in range(4))


def leer_diario(f: Path) -> list[dict]:
    if not f.exists():
        return []
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def evaluar_frenos(diario: list[dict], piezas: pd.DataFrame) -> list[dict]:
    """Decision 11.3: cada freno se compara con lo que hizo la pieza desde su ejecucion hasta la siguiente senyal."""
    out = []
    senyales = [pd.Timestamp(d["senyal"][:10]) for d in diario]
    for i, d in enumerate(diario):
        for pieza, motivo in d.get("frenos", []):
            ini = P.dia_de_ejecucion(piezas, pd.Timestamp(d["senyal"][:10])) if pd.Timestamp(d["senyal"][:10]) in piezas.index else None
            if ini is None:
                continue
            fin_s = senyales[i + 1] if i + 1 < len(senyales) else piezas.index[-1]
            tramo = piezas[pieza].loc[ini:fin_s]
            cambio = float(tramo.iloc[-1] / tramo.iloc[0] - 1) if len(tramo) > 1 else 0.0
            out.append({"senyal": d["senyal"][:10], "pieza": pieza, "motivo": motivo, "cambio": cambio,
                        "acierto": cambio < 0, "cerrado": i + 1 < len(senyales)})
    return out


def generar(base: Path, ahora: datetime) -> str:
    estado = json.loads((base / "estado.json").read_text(encoding="utf-8")) if (base / "estado.json").exists() else {}
    config = json.loads((base / "papel.json").read_text(encoding="utf-8")) if (base / "papel.json").exists() else {}
    control = json.loads((base / "control.json").read_text(encoding="utf-8")) if (base / "control.json").exists() else {}
    cierres = precios.tabla(precios.leer(base / "precios.csv"))
    diario = leer_diario(base / "ia_diario.jsonl")
    pausa = bool(control.get("pausa"))
    secciones = []
    p = None
    if config and not cierres.empty:
        try:
            hasta = min(pd.Timestamp(ahora.date()), P.ultimo_dia_completo(cierres))
            p = P.calcular(cierres, pd.Timestamp(config["primera_senyal"]), hasta)
        except ValueError:
            p = None
    piezas = P.piezas_de(cierres) if not cierres.empty else pd.DataFrame()

    # Resumen
    if p is not None:
        ganancia = p.valor_eur / P.CAPITAL_EUR - 1
        ref = p.referencia_eur / P.CAPITAL_EUR - 1
        graves = [i for i in estado.get("incidencias", []) if i.get("grave")]
        proxima = p.hasta + pd.offsets.BMonthEnd(0) if p.hasta != p.hasta + pd.offsets.BMonthEnd(0) else p.hasta + pd.offsets.BMonthEnd(1)
        tarjetas = [tarjeta("Valor (papel)", m.eur(p.valor_eur), f"{m.pct(ganancia, True)} desde el inicio"),
                    tarjeta("VWCE mantenido", m.eur(p.referencia_eur), f"{m.pct(ref, True)} desde el inicio"),
                    tarjeta("Peor caída", m.pct(p.caida), "límite 14,9 %"),
                    tarjeta("Próxima revisión", f"{proxima:%d/%m/%Y}", f"datos hasta el {p.hasta:%d/%m/%Y}"),
                    tarjeta("Salud", "⚠️ " + str(len(graves)) + " grave(s)" if graves else "Todo bien",
                            "pausa activada (sin efecto en papel)" if pausa else "sin pausa")]
        filas = "".join(f"<tr><td>{e(m.NOMBRES[k])}</td><td>{puntos_html(p.puntos.get(k, 0))}</td><td>{m.pct(w)}</td></tr>"
                        for k, w in p.pesos.items())
        filas += f"<tr><td>{e(m.NOMBRES['monetario'])}</td><td>-</td><td>{m.pct(max(0.0, 1 - sum(p.pesos.values())))}</td></tr>"
        ia_ult = estado.get("ia") or {}
        resumen = (f'<div class="tarjetas">{"".join(tarjetas)}</div>'
                   f'<table><tr><th>Pieza</th><th>Medias superadas</th><th>Peso</th></tr>{filas}</table>'
                   f'<p class="ia"><b>La IA</b> ({e(ia_ult.get("senyal", "-"))}): '
                   f'{e(ia_ult.get("explicacion") or ia_ult.get("motivo") or "sin respuesta todavía")}</p>')
    else:
        resumen = ('<p class="vacio">El papel aún no ha empezado'
                   + (f' (primera señal: {e(config["primera_senyal"])})' if config else "") + ".</p>")
    secciones.append(("Resumen", resumen))

    # 1. Valor frente al indexado, y caidas
    if p is not None:
        v = p.valor * P.CAPITAL_EUR
        r = p.referencia * P.CAPITAL_EUR
        caida = -(1 - p.valor / p.valor.cummax()) * 100
        secciones.append(("1. Valor frente al indexado", svg_lineas(
            [("Papel", v, VERDE, "continuo"), ("VWCE", r, GRIS, "discontinuo")], formato=lambda x: f"{x:,.0f} €")
            + svg_lineas([("Caída", caida, VERDE, "continuo")], alto=140, formato=lambda x: f"{x:.0f} %")))
    # 2. Cada pieza con sus 4 medias
    if not piezas.empty:
        graf = []
        for k in P.PIEZAS:
            s = piezas[k].dropna()
            series = [(m.NOMBRES[k].split(" ")[0], s.iloc[-260:], TINTA, "continuo")]
            for mm, color in zip(E.MEDIAS, RAMPA_MEDIAS, strict=True):
                series.append((f"media {mm}", s.rolling(mm).mean().iloc[-260:], color, "continuo"))
            graf.append(f"<h3>{e(m.NOMBRES[k])}</h3>" + svg_lineas(series, alto=200, formato=lambda x: f"{x:,.2f}"))
        secciones.append(("2. Cada pieza con sus 4 medias", "".join(graf)))
    # 3. Operaciones
    ops = estado.get("operaciones", [])
    filas = "".join(f"<tr><td>{e(o['fecha'])}</td><td>{e(m.NOMBRES[o['pieza']])}</td><td>{'compra' if o['despues'] > o['antes'] else 'venta'}</td>"
                    f"<td>{m.pct(o['antes'])} → {m.pct(o['despues'])}</td></tr>" for o in reversed(ops))
    secciones.append(("3. Operaciones", f"<table><tr><th>Fecha</th><th>Pieza</th><th>Tipo</th><th>Peso</th></tr>{filas}</table>"
                      if ops else '<p class="vacio">Ninguna todavía.</p>'))
    # 4. Historial de la IA
    filas = "".join(f"<tr><td>{e(d['senyal'][:10])}</td><td>{e(d.get('explicacion') or d.get('motivo'))}</td>"
                    f"<td>{e('; '.join(f'{a}: {b}' for a, b in d.get('frenos', [])) or '-')}</td></tr>" for d in reversed(diario))
    secciones.append(("4. Historial de la IA", f"<table><tr><th>Señal</th><th>Explicación</th><th>Frenaría</th></tr>{filas}</table>"
                      if diario else '<p class="vacio">Ninguna señal todavía.</p>'))
    # 5. Con y sin la IA
    frenos = evaluar_frenos(diario, piezas) if not piezas.empty else []
    if frenos:
        filas = "".join(f"<tr><td>{e(f['senyal'])}</td><td>{e(m.NOMBRES[f['pieza']])}</td><td>{m.pct(f['cambio'], True)}</td>"
                        f"<td>{'acertó' if f['acierto'] else 'falló'}{'' if f['cerrado'] else ' (provisional)'}</td></tr>" for f in frenos)
        cerrados = [f for f in frenos if f["cerrado"]]
        nota = (f"{sum(f['acierto'] for f in cerrados)} de {len(cerrados)} aciertos cerrados. La IA gana voz solo con "
                "al menos 5 casos, acierto en la mayoría, evitando pérdidas de media y el sí del propietario (11.3).")
        secciones.append(("5. Con y sin la IA", f"<table><tr><th>Señal</th><th>Pieza</th><th>La pieza hizo</th><th>Freno</th></tr>"
                          f"{filas}</table><p>{e(nota)}</p>"))
    else:
        secciones.append(("5. Con y sin la IA", '<p class="vacio">La IA no ha frenado ninguna compra todavía.</p>'))
    # 6. Hacienda
    if p is not None:
        secciones.append(("6. Hacienda (simulada)", f"<p>En papel no hay dinero real: no hay nada que declarar. "
                          f"Impuestos simulados (incluido lo que se pagaría si se vendiera hoy): {m.eur(p.impuestos_eur)}. "
                          f"Si se vendiera todo hoy, quedarían {m.eur(p.si_vende_hoy_eur)}.</p>"))

    logo = LOGO.read_text(encoding="utf-8") if LOGO.exists() else ""
    boton = ('<button data-accion="reanudar">Reanudar</button>' if pausa else '<button data-accion="pausa">Pausar</button>')
    cuerpo = "".join(f"<section><h2>{e(t)}</h2>{c}</section>" for t, c in secciones)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ebisu</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#1E5E57"><meta name="apple-mobile-web-app-title" content="Ebisu"><style>
:root{{--verde:{VERDE};--oro:{ORO};--crema:{CREMA};--tinta:{TINTA};--gris:{GRIS}}}
body{{margin:0;background:var(--crema);color:var(--tinta);font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{background:var(--verde);color:var(--crema);display:flex;align-items:center;gap:14px;padding:12px 16px}}
header svg{{width:44px;height:44px}} header h1{{font-size:20px;margin:0}} header .sub{{opacity:.85;font-size:13px}}
main{{max-width:900px;margin:0 auto;padding:12px 16px 40px}} section{{background:#fff;border-radius:10px;padding:14px 16px;margin:14px 0}}
h2{{font-size:17px;margin:0 0 10px;color:var(--verde)}} h3{{font-size:14px;margin:12px 0 4px}}
.tarjetas{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:12px}}
.tarjeta{{border:1px solid #e3e0d6;border-radius:8px;padding:8px 10px}} .t{{font-size:12px;color:var(--gris)}} .v{{font-size:20px;font-weight:600}} .n{{font-size:12px;color:var(--gris)}}
table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{text-align:left;padding:5px 6px;border-bottom:1px solid #eee;vertical-align:top}}
.punto{{display:inline-block;width:10px;height:10px;border-radius:50%;border:2px solid var(--verde);margin-right:3px}} .punto.lleno{{background:var(--verde)}}
.grafico{{width:100%;height:auto}} .rejilla{{stroke:#e6e3da;stroke-width:1}} .eje{{fill:var(--gris);font-size:11px}} .etiqueta{{fill:var(--tinta);font-size:12px}}
.vacio{{color:var(--gris)}} .ia{{background:var(--crema);border-left:4px solid var(--oro);padding:8px 10px;border-radius:4px}}
button{{background:var(--verde);color:var(--crema);border:0;border-radius:6px;padding:8px 14px;font-size:14px;cursor:pointer}}
footer{{text-align:center;color:var(--gris);font-size:12px}}
</style></head><body><header>{logo}<div><h1>Ebisu</h1><div class="sub">H1-M · actualizado el {ahora:%d/%m/%Y %H:%M}</div></div>
<div style="margin-left:auto">{boton}</div></header><main>{cuerpo}</main>
<footer>Papel: sin dinero real. La pausa no actúa en papel.</footer><script src="/panel.js"></script></body></html>"""


def escribir(base: Path, ahora: datetime) -> Path:
    f = base / "panel.html"
    tmp = f.with_suffix(".tmp")
    tmp.write_text(generar(base, ahora), encoding="utf-8")
    tmp.replace(f)
    return f
