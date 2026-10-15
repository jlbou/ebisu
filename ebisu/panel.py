"""El panel del bot en papel (decision 9; P5; docs/plan-bot-papel.md): una pagina tipo informe que se rehace al final de
cada vuelta y al pulsar un boton. Disenyo del 15/10/2026 (skill `frontend-design`, plan aprobado por el propietario).

Arriba, lo que hace la regla este mes (las tres piezas con sus 4 medias como boyas y su peso; antes de empezar el papel,
lo que haria si hoy fuera dia de senyal) y una franja de salud (ultima vuelta, la IA, la copia, el latido). Debajo, por
orden: el valor frente al indexado y las caidas; cada pieza con sus 4 medias; operaciones; la IA mes a mes; con y sin la
IA (cada freno, en sombra: acerto si la pieza bajo); Hacienda (simulada). En castellano y "la IA", nunca el modelo.

Los graficos los dibuja `panel.js` en el navegador (Lightweight Charts, en `ebisu/vendor/`) con los datos que la pagina
lleva dentro en JSON; sin dependencias nuevas de Python. Colores: los del logo y sus derivados.
"""

from __future__ import annotations

import csv
import html
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from ebisu import estrategia as E
from ebisu import ia
from ebisu import mensajes as m
from ebisu import papel as P
from ebisu import precios

RAIZ = Path(__file__).resolve().parents[1]
LOGO = RAIZ / "assets" / "logo" / "favicon.svg"
COPIAS = Path("/var/backups/ebisu")
DIAS_GRAFICO_PIEZAS = 260  # un anyo de bolsa
NOMBRES_CORTOS = {"bolsa": "Bolsa mundial", "bonos": "Bonos de EE. UU. en euros", "oro": "Oro",
                  "monetario": "Monetario"}


def e(x: object) -> str:
    return html.escape(re.sub(r"(?i)claude", "la IA", str(x)))


def fecha(d: str | pd.Timestamp | datetime | None) -> str:
    if d is None or d == "":
        return "-"
    return f"{pd.Timestamp(d):%d/%m/%Y}"


def serie_json(s: pd.Series, redondeo: int = 4) -> list[dict]:
    s = s.dropna()
    return [{"time": f"{d:%Y-%m-%d}", "value": round(float(v), redondeo)} for d, v in s.items()]


def boyas(n: int | None) -> str:
    if n is None:
        return '<span class="boyas sin">sin datos</span>'
    llenas = "".join('<span class="boya llena"></span>' if i < n else '<span class="boya"></span>' for i in range(4))
    return f'<span class="boyas" role="img" aria-label="{n} de 4 medias superadas">{llenas}</span>'


def leer_diario(f: Path) -> list[dict]:
    if not f.exists():
        return []
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def ultima_vuelta(base: Path) -> dict | None:
    f = base / "vueltas.csv"
    if not f.exists():
        return None
    with f.open(encoding="utf-8") as h:
        filas = list(csv.DictReader(h))
    return filas[-1] if filas else None


def ultima_copia(directorio: Path = COPIAS) -> pd.Timestamp | None:
    try:
        fechas = [re.search(r"\d{4}-\d{2}-\d{2}", f.name) for f in directorio.glob("ebisu-*.tar.gz")]
    except OSError:
        return None
    fechas = [pd.Timestamp(x.group(0)) for x in fechas if x]
    return max(fechas) if fechas else None


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


def salud(base: Path, estado: dict, ahora: datetime, copias: Path = COPIAS) -> list[tuple[str, str, str]]:
    """La franja de salud: (estado, texto, detalle). estado: ok | aviso | mal | nada."""
    hoy = pd.Timestamp(ahora.date())
    out = []
    v = ultima_vuelta(base)
    if v is None:
        out.append(("nada", "Sin vueltas todavía", "La primera es hoy a las 20:05."))
    else:
        hora = pd.Timestamp(v["hora"])
        antigua = (hoy - pd.Timestamp(hora.date())).days > 1
        if v["ok"] != "1":
            out.append(("mal", f"La vuelta del {fecha(hora)} falló", "Mira el aviso de Telegram con el detalle."))
        elif antigua:
            out.append(("aviso", f"Última vuelta: {fecha(hora)}", "Lleva más de un día sin dar la vuelta."))
        else:
            out.append(("ok", f"Última vuelta a las {hora:%H:%M}", fecha(hora)))
    if "ia_version" not in estado:
        out.append(("nada", "La IA, sin comprobar", "Se comprueba en cada vuelta."))
    elif estado["ia_version"] == ia.VERSION_VERIFICADA:
        out.append(("ok", "La IA responde", f"versión {ia.VERSION_VERIFICADA}"))
    else:
        out.append(("mal", "La IA no responde", "Revisa el token de la IA en el .env del servidor."))
    c = ultima_copia(copias)
    if c is None:
        out.append(("nada", "Copia: sin dato aquí", "Las copias están en el servidor."))
    elif (hoy - c).days > 2:
        out.append(("mal", f"Última copia: {fecha(c)}", "Hace más de dos días: revisa ebisu-copia."))
    else:
        out.append(("ok", "Copia al día", fecha(c)))
    if "latido" not in estado:
        out.append(("nada", "Latido, sin dato", "Se anota en cada vuelta."))
    elif estado["latido"] is True:
        out.append(("ok", "Latido enviado", "Healthchecks: ebisu-dia"))
    elif estado["latido"] is None:
        out.append(("aviso", "Sin latido", "Falta HEALTHCHECK_EBISU en el .env del servidor."))
    else:
        out.append(("mal", "El latido no llegó", "Healthchecks avisará si sigue así."))
    graves = [i for i in estado.get("incidencias", []) if i.get("grave")]
    if graves:
        out.append(("mal", f"{len(graves)} incidencia(s) grave(s)", "; ".join(i["texto"] for i in graves)[:200]))
    return out


def generar(base: Path, ahora: datetime, copias: Path = COPIAS) -> str:
    estado = json.loads((base / "estado.json").read_text(encoding="utf-8")) if (base / "estado.json").exists() else {}
    config = json.loads((base / "papel.json").read_text(encoding="utf-8")) if (base / "papel.json").exists() else {}
    control = json.loads((base / "control.json").read_text(encoding="utf-8")) if (base / "control.json").exists() else {}
    cierres = precios.tabla(precios.leer(base / "precios.csv"))
    diario = leer_diario(base / "ia_diario.jsonl")
    pausa = bool(control.get("pausa"))
    p = None
    if config and not cierres.empty:
        try:
            hasta = min(pd.Timestamp(ahora.date()), P.ultimo_dia_completo(cierres))
            p = P.calcular(cierres, pd.Timestamp(config["primera_senyal"]), hasta)
        except ValueError:
            p = None
    piezas = P.piezas_de(cierres) if not cierres.empty else pd.DataFrame()
    datos: dict = {"piezas": {}}

    # La regla: este mes (papel en marcha) o "si hoy fuera dia de senyal" (antes de empezar)
    pesos, puntos, nota = {}, {}, ""
    if p is not None:
        titulo = "Este mes"
        pesos, puntos = p.pesos, p.puntos
        proxima = p.hasta + pd.offsets.BMonthEnd(0) if p.hasta != p.hasta + pd.offsets.BMonthEnd(0) else p.hasta + pd.offsets.BMonthEnd(1)
        nota = f"Señal del {fecha(p.ultima_senyal)}. Próxima revisión: {fecha(proxima)}."
    elif not piezas.empty and len(piezas) >= max(E.MEDIAS):
        titulo = "Si hoy fuera día de señal"
        objetivo = E.pesos_objetivo(piezas, P.H1M)
        if len(objetivo):
            pesos = {k: float(objetivo.iloc[-1][k]) for k in P.PIEZAS}
        for k in P.PIEZAS:
            n = E.medias_superadas(piezas[k]).iloc[-1]
            puntos[k] = None if pd.isna(n) else int(n)
        nota = (f"El papel aún no ha empezado{' (primera señal: ' + fecha(config['primera_senyal']) + ')' if config else ''}. "
                f"Con los precios del {fecha(piezas.index[-1])}, la regla quedaría así.")
    else:
        titulo = "Todavía sin precios"
        nota = "La vuelta del día baja los precios de los ETF a partir de las 20:05."
    filas = ""
    if pesos:
        for k in P.PIEZAS:
            filas += (f'<div class="fila"><span class="pieza">{e(NOMBRES_CORTOS[k])}</span>{boyas(puntos.get(k))}'
                      f'<span class="peso">{m.pct(pesos.get(k, 0.0))}</span></div>')
        filas += (f'<div class="fila monetario"><span class="pieza">{e(NOMBRES_CORTOS["monetario"])}</span><span></span>'
                  f'<span class="peso">{m.pct(max(0.0, 1 - sum(pesos.values())))}</span></div>')
    regla = f'<section class="regla" aria-labelledby="t-regla"><h2 id="t-regla">{e(titulo)}</h2>{filas}<p>{e(nota)}</p></section>'

    chips = "".join(f'<li class="chip {c}"><b>{e(t)}</b><span>{e(d)}</span></li>' for c, t, d in salud(base, estado, ahora, copias))
    if pausa:
        chips += '<li class="chip aviso"><b>Pausa activada</b><span>En papel no tiene efecto.</span></li>'
    franja = f'<ul class="salud" aria-label="Salud del bot">{chips}</ul>'

    secciones = []
    # Valor frente al indexado, y caidas
    if p is not None:
        v, r = p.valor * P.CAPITAL_EUR, p.referencia * P.CAPITAL_EUR
        datos.update({"valor": serie_json(v, 2), "referencia": serie_json(r, 2),
                      "caida": serie_json(-(1 - p.valor / p.valor.cummax()) * 100, 2)})
        ganancia, ref = p.valor_eur / P.CAPITAL_EUR - 1, p.referencia_eur / P.CAPITAL_EUR - 1
        cifras = (f'<p class="cifras"><span><b>{m.eur(p.valor_eur)}</b> Ebisu, {m.pct(ganancia, True)}</span>'
                  f'<span><b>{m.eur(p.referencia_eur)}</b> el indexado (VWCE) mantenido, {m.pct(ref, True)}</span>'
                  f'<span><b>{m.pct(p.caida)}</b> peor caída (límite: 14,9 %)</span></p>')
        cuerpo = (cifras + '<div class="leyenda"><span class="l-ebisu">Ebisu</span><span class="l-ref">Indexado (VWCE)</span></div>'
                  '<div class="grafico grande" id="g-valor"></div><h3>Caída desde el máximo</h3>'
                  '<div class="grafico bajo" id="g-caida"></div>')
    else:
        cuerpo = '<p class="vacio">Aparecerá con el papel: el valor de Ebisu día a día frente al indexado mantenido.</p>'
    secciones.append(("t-valor", "Valor frente al indexado", cuerpo))

    # Cada pieza con sus 4 medias
    if not piezas.empty:
        graf = []
        for k in P.PIEZAS:
            s = piezas[k].dropna()
            datos["piezas"][k] = {"precio": serie_json(s.iloc[-DIAS_GRAFICO_PIEZAS:]),
                                  "medias": {str(mm): serie_json(s.rolling(mm).mean().iloc[-DIAS_GRAFICO_PIEZAS:])
                                             for mm in E.MEDIAS}}
            graf.append(f'<div class="pieza-graf"><h3>{e(NOMBRES_CORTOS[k])} {boyas(puntos.get(k))}</h3>'
                        f'<div class="grafico" id="g-{k}"></div></div>')
        cuerpo = ('<div class="leyenda"><span class="l-precio">Precio</span><span class="l-m20">Media de 20 días</span>'
                  '<span class="l-m50">50</span><span class="l-m100">100</span><span class="l-m200">200</span></div>'
                  + "".join(graf))
    else:
        cuerpo = '<p class="vacio">Aparecerá con los primeros precios guardados.</p>'
    secciones.append(("t-piezas", "Cada pieza con sus medias", cuerpo))

    # Operaciones
    ops = estado.get("operaciones", [])
    if ops:
        filas = "".join(f"<tr><td>{fecha(o['fecha'])}</td><td>{e(NOMBRES_CORTOS[o['pieza']])}</td>"
                        f"<td>{'Compra' if o['despues'] > o['antes'] else 'Venta'}</td>"
                        f"<td class='num'>{m.pct(o['antes'])} a {m.pct(o['despues'])}</td></tr>" for o in reversed(ops))
        cuerpo = (f'<div class="tabla"><table><thead><tr><th>Fecha</th><th>Pieza</th><th>Tipo</th><th class="num">Peso</th>'
                  f'</tr></thead><tbody>{filas}</tbody></table></div>')
    else:
        cuerpo = '<p class="vacio">Ninguna todavía. Las primeras llegan el día hábil siguiente a la primera señal.</p>'
    secciones.append(("t-ops", "Operaciones", cuerpo))

    # La IA, mes a mes
    if diario:
        items = "".join(f'<li><time>{fecha(d["senyal"][:10])}</time><p>{e(d.get("explicacion") or d.get("motivo"))}</p>'
                        + (f'<p class="freno">Frenaría: {e("; ".join(f"{NOMBRES_CORTOS.get(a, a)}: {b}" for a, b in d["frenos"]))}</p>'
                           if d.get("frenos") else "") + "</li>" for d in reversed(diario))
        cuerpo = f'<ol class="ia-lista">{items}</ol>'
    else:
        cuerpo = '<p class="vacio">La IA explica cada señal mensual. La primera llegará con la primera señal del papel.</p>'
    secciones.append(("t-ia", "La IA, mes a mes", cuerpo))

    # Con y sin la IA
    frenos = evaluar_frenos(diario, piezas) if not piezas.empty else []
    if frenos:
        filas = "".join(f"<tr><td>{fecha(f['senyal'])}</td><td>{e(NOMBRES_CORTOS[f['pieza']])}</td>"
                        f"<td class='num'>{m.pct(f['cambio'], True)}</td>"
                        f"<td>{'Acertó' if f['acierto'] else 'Falló'}{'' if f['cerrado'] else ' (provisional)'}</td></tr>"
                        for f in frenos)
        cerrados = [f for f in frenos if f["cerrado"]]
        cuerpo = (f'<div class="tabla"><table><thead><tr><th>Señal</th><th>Pieza frenada</th><th class="num">La pieza hizo</th>'
                  f'<th>Freno</th></tr></thead><tbody>{filas}</tbody></table></div>'
                  f'<p>{sum(f["acierto"] for f in cerrados)} aciertos de {len(cerrados)} casos cerrados. La IA gana voz solo con '
                  'al menos 5 casos, acierto en la mayoría, evitando pérdidas de media y el sí del propietario (decisión 11.3).</p>')
    else:
        cuerpo = ('<p class="vacio">La IA no ha frenado ninguna compra todavía. Cada freno se apunta en sombra y aquí se ve '
                  'si habría acertado.</p>')
    secciones.append(("t-con-sin", "Con y sin la IA", cuerpo))

    # Hacienda
    if p is not None:
        cuerpo = (f"<p>En papel no hay dinero real: no hay nada que declarar. Impuestos simulados, incluido lo que se pagaría "
                  f"si se vendiera hoy: <b>{m.eur(p.impuestos_eur)}</b>. Si se vendiera todo hoy, quedarían "
                  f"<b>{m.eur(p.si_vende_hoy_eur)}</b>.</p>")
    else:
        cuerpo = '<p class="vacio">Aparecerá con el papel: los impuestos simulados de cada año.</p>'
    secciones.append(("t-hacienda", "Hacienda (simulada)", cuerpo))

    logo = re.sub(r"<title>.*?</title>", "", LOGO.read_text(encoding="utf-8")) if LOGO.exists() else ""
    logo = logo.replace('role="img" aria-label="Ebisu"', 'aria-hidden="true"')
    boton = ('<button type="button" data-accion="reanudar">Reanudar</button>' if pausa
             else '<button type="button" data-accion="pausa">Pausar</button>')
    cuerpo = "".join(f'<section aria-labelledby="{i}"><h2 id="{i}">{e(t)}</h2>{c}</section>' for i, t, c in secciones)
    datos_json = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ebisu</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#F2F5F3"><meta name="apple-mobile-web-app-title" content="Ebisu">
<link rel="preload" href="/vendor/atkinson-400.woff2" as="font" type="font/woff2" crossorigin><style>{CSS}</style></head>
<body><a class="saltar" href="#contenido">Ir al contenido</a>
<header><div class="marca">{logo}<h1 translate="no">Ebisu</h1></div><p class="actualizado">Actualizado el {ahora:%d/%m/%Y} a las {ahora:%H:%M}</p>{boton}</header>
<main id="contenido">{regla}{franja}{cuerpo}</main>
<footer>En papel: sin dinero real. Pausar no tiene efecto mientras dure el papel.</footer>
<script type="application/json" id="datos">{datos_json}</script>
<script src="/vendor/lightweight-charts.js"></script><script src="/panel.js"></script></body></html>"""


CSS = """
@font-face{font-family:"Atkinson Hyperlegible";src:url(/vendor/atkinson-400.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Atkinson Hyperlegible";src:url(/vendor/atkinson-700.woff2) format("woff2");font-weight:700;font-display:swap}
:root{--verde:#1E5E57;--verde-hondo:#143F3A;--verde-medio:#2F786D;--verde-claro:#9CC7BF;--agua:#DCE7E3;--fondo:#F2F5F3;
--oro:#E3B341;--oro-hondo:#9A7317;--oro-claro:#FBF1D6;--crema:#F3F1EA;--tinta:#1F2A28;--gris:#53625E;--rojo:#B5483B;
--rojo-claro:#F7E4E0;--blanco:#FFFFFF}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--fondo);color:var(--tinta);font:16px/1.5 "Atkinson Hyperlegible",system-ui,sans-serif}
a{color:var(--verde)}
:focus-visible{outline:3px solid var(--oro);outline-offset:2px}
.saltar{position:absolute;left:-999px}.saltar:focus{left:16px;top:8px;background:var(--blanco);padding:6px 10px;z-index:9}
header{display:flex;align-items:center;gap:16px;flex-wrap:wrap;max-width:1040px;margin:0 auto;padding:20px 16px 12px}
.marca{display:flex;align-items:center;gap:12px}
.marca svg{width:44px;height:44px;display:block}
h1,h2,h3{text-wrap:balance}
h2{scroll-margin-top:16px}
h1{font-size:30px;line-height:1;margin:0;color:var(--verde-hondo);letter-spacing:-.01em}
.actualizado{margin:0;color:var(--gris);font-size:14px}
header button{margin-left:auto}
button{font:inherit;font-weight:700;background:var(--blanco);color:var(--verde-hondo);border:2px solid var(--verde);
border-radius:999px;padding:6px 18px;cursor:pointer;min-height:40px;touch-action:manipulation;
-webkit-tap-highlight-color:transparent;transition:background-color .15s,color .15s}
button:hover{background:var(--verde);color:var(--crema)}
main{max-width:1040px;margin:0 auto;padding:0 16px 40px}
.regla{background:var(--verde);color:var(--crema);border-radius:20px;padding:24px 28px 20px;margin:4px 0 14px}
.regla h2{color:var(--crema);font-size:22px;margin:0 0 14px}
.fila{display:grid;grid-template-columns:minmax(0,1fr) auto 72px;align-items:center;gap:16px;padding:10px 0;
border-bottom:1px solid rgba(243,241,234,.18);font-size:19px}
.fila.monetario{border-bottom:0;color:rgba(243,241,234,.85)}
.peso{font-weight:700;text-align:right;font-variant-numeric:tabular-nums}
.regla p{margin:12px 0 0;color:rgba(243,241,234,.85);font-size:15px;max-width:70ch}
.boyas{display:inline-flex;gap:8px;vertical-align:middle}
.boya{width:20px;height:20px;border-radius:50%;border:2px solid rgba(243,241,234,.55)}
.boya.llena{background:var(--oro);border-color:var(--oro)}
.boyas.sin{font-size:14px;opacity:.8}
.salud{list-style:none;margin:0 0 28px;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.chip{display:flex;flex-direction:column;padding:8px 14px 8px 32px;border-radius:12px;background:var(--blanco);
border:1px solid var(--agua);position:relative;font-size:14px;min-width:150px}
.chip b,.chip span{overflow-wrap:anywhere}.chip b{font-weight:700}.chip span{color:var(--gris);font-size:13px}
.chip::before{content:"";position:absolute;left:12px;top:14px;width:10px;height:10px;border-radius:50%;background:var(--gris)}
.chip.ok::before{background:var(--verde-medio)}
.chip.aviso{background:var(--oro-claro);border-color:#EED9A0}.chip.aviso::before{background:var(--oro-hondo)}
.chip.mal{background:var(--rojo-claro);border-color:#E9BDB5}.chip.mal::before{background:var(--rojo)}
.chip.nada::before{background:transparent;border:2px solid var(--gris);width:6px;height:6px}
section{margin:0 0 32px}
section>h2{font-size:22px;color:var(--verde-hondo);margin:0 0 12px}
h3{font-size:17px;margin:18px 0 6px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
h3 .boya{width:14px;height:14px;border-color:var(--verde-claro)}h3 .boya.llena{border-color:var(--oro)}
.cifras{display:flex;flex-wrap:wrap;gap:8px 28px;margin:0 0 12px;max-width:none}
.cifras b{font-size:22px;font-variant-numeric:tabular-nums;margin-right:6px}
.grafico{height:240px;background:var(--blanco);border:1px solid var(--agua);border-radius:14px;overflow:hidden}
.grafico.grande{height:340px}.grafico.bajo{height:150px}
.leyenda{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:14px;color:var(--gris);margin:0 0 8px}
.leyenda span::before{content:"";display:inline-block;width:18px;height:0;border-top:3px solid;vertical-align:middle;margin-right:6px}
.l-ebisu::before{color:#C9971F}.l-ref::before{color:var(--gris);border-top-style:dashed!important}
.l-precio::before{color:var(--tinta)}.l-m20::before{color:#A9D2C8}.l-m50::before{color:#6FB0A3}.l-m100::before{color:#2F786D}
.l-m200::before{color:#C9971F}
.tabla{overflow-x:auto;background:var(--blanco);border:1px solid var(--agua);border-radius:14px}
table{width:100%;border-collapse:collapse;font-size:15px}
th,td{text-align:left;padding:10px 14px;border-bottom:1px solid var(--agua);vertical-align:top;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
th{color:var(--gris);font-weight:700;font-size:14px}
.num{text-align:right;font-variant-numeric:tabular-nums}
.ia-lista{list-style:none;margin:0;padding:0;border-left:3px solid var(--oro);max-width:75ch}
.ia-lista li{padding:0 0 16px 18px}
.ia-lista time{font-weight:700;color:var(--verde-hondo)}
.ia-lista p{margin:4px 0 0;overflow-wrap:break-word}.ia-lista .freno{color:var(--rojo)}
.vacio{color:var(--gris);margin:0;max-width:70ch}
footer{max-width:1040px;margin:0 auto;padding:0 16px 32px;color:var(--gris);font-size:14px}
@media (max-width:600px){
  h1{font-size:26px}.regla{padding:18px 16px;border-radius:16px}
  .fila{grid-template-columns:minmax(0,1fr) 56px;font-size:17px;row-gap:6px}
  .fila .boyas{grid-column:1;grid-row:2}.fila .peso{grid-column:2;grid-row:1/span 2}
  .boya{width:18px;height:18px}.grafico.grande{height:260px}.chip{min-width:0;flex:1 1 140px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""


def escribir(base: Path, ahora: datetime) -> Path:
    f = base / "panel.html"
    tmp = f.with_suffix(".tmp")
    tmp.write_text(generar(base, ahora), encoding="utf-8")
    tmp.replace(f)
    return f
