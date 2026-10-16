"""La vuelta de cada dia del bot en papel (docs/plan-bot-papel.md 3): une todas las piezas.

    python -m ebisu.dia                     # la vuelta del dia (la lanza el temporizador, todos los dias a las 20:00)
    python -m ebisu.dia --seco              # con datos reales, sin Telegram, sin latido y sin guardar nada
    python -m ebisu.dia --empezar 2026-10-30   # fija la primera senyal del papel y la huella (una sola vez)

Orden: precios -> titulares -> si hay senyal nueva, la IA en sombra -> papel -> juez -> avisos (a la cola) -> estado
-> cola a Telegram -> latido. Cada aviso tiene una clave: rehacer el dia no repite nada. NUNCA se cae sin avisar: si
algo revienta, latido de fallo y aviso de incidencia.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import tempfile
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from ebisu import cola, ia, juez, latido, mensajes, noticias, panel, papel, precios, secretos, telegram
from ebisu.papel_huella import huella

RAIZ = Path(__file__).resolve().parents[1]
VAR = RAIZ / "var" / "bot"
log = logging.getLogger("ebisu.dia")


@dataclass
class Dependencias:
    """Todo lo de fuera, para poder probar la vuelta sin red (las pruebas lo sustituyen)."""
    fuente_precios: precios.Fuente = precios.yahoo
    bajar_rss: Callable[[str], bytes] = noticias.bajar
    preguntar_ia: Callable[..., ia.Respuesta] = ia.preguntar
    mandar: Callable[[str], bool] | None = None  # None = Telegram con los secretos
    latido_ok: Callable[[str | None], Any] = latido.todo_bien
    latido_fallo: Callable[[str | None], Any] = latido.fallo
    comprobar_ia: Callable[[str | None], str | None] = ia.comprobar
    secretos: secretos.Secretos = field(default_factory=secretos.leer)


def _escribir_json(fichero: Path, datos: dict) -> None:
    fichero.parent.mkdir(parents=True, exist_ok=True)
    tmp = fichero.with_suffix(".tmp")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, fichero)


def _leer_json(fichero: Path) -> dict:
    return json.loads(fichero.read_text(encoding="utf-8")) if fichero.exists() else {}


def empezar(base: Path, primera_senyal: str) -> dict:
    """Fija la primera senyal y la huella de la estrategia. Una sola vez."""
    f = base / "papel.json"
    if f.exists():
        raise SystemExit(f"El papel ya empezo ({_leer_json(f)}): no se cambia.")
    datos = {"primera_senyal": primera_senyal, "huella": huella(), "fijado": datetime.now(precios.MADRID).isoformat()}
    _escribir_json(f, datos)
    return datos


def dias_con_vuelta(base: Path) -> set[pd.Timestamp]:
    f = base / "vueltas.csv"
    if not f.exists():
        return set()
    with f.open(encoding="utf-8") as h:
        return {pd.Timestamp(r["fecha"]) for r in csv.DictReader(h) if r["ok"] == "1"}


def apuntar_vuelta(base: Path, ahora: datetime, ok: bool, resumen: str) -> None:
    f = base / "vueltas.csv"
    nuevo = not f.exists()
    with f.open("a", newline="", encoding="utf-8") as h:
        w = csv.writer(h, lineterminator="\n")
        if nuevo:
            w.writerow(["fecha", "ok", "hora", "resumen"])
        w.writerow([ahora.date().isoformat(), int(ok), ahora.isoformat(timespec="seconds"), resumen[:300]])


def vuelta(ahora: datetime, base: Path = VAR, dep: Dependencias | None = None) -> dict:
    """Una vuelta. Devuelve el estado guardado. Lanza solo si algo revienta (lo recoge `principal`)."""
    dep = dep or Dependencias()
    base.mkdir(parents=True, exist_ok=True)
    hoy = pd.Timestamp(ahora.date())
    f_cola = base / "cola.json"
    apuntados = []

    def aviso(clave: str, texto: str) -> None:
        if cola.apuntar(f_cola, clave, texto, ahora):
            apuntados.append(clave)

    empezado = bool(_leer_json(base / "papel.json"))  # antes de empezar se rellenan los dias que falten (16/10)
    cierres, avisos_precios = precios.actualizar(base / "precios.csv", ahora, dep.fuente_precios,
                                                 rellenar_huecos=not empezado)
    n_titulares, errores_rss = noticias.recoger(base / "noticias.csv", ahora, dep.bajar_rss)
    if len(errores_rss) == len(noticias.FUENTES):
        aviso(f"rss:{hoy.date()}", mensajes.incidencia(juez.Incidencia(False, "noticias", "ninguna fuente respondio")))

    config = _leer_json(base / "papel.json")
    estado = _leer_json(base / "estado.json")
    estado.update({"ultima_vuelta": ahora.isoformat(timespec="seconds"), "empezado": bool(config)})
    if not config:
        for a in avisos_precios:
            aviso(f"precios:{a.tipo}:{a.pieza}:{a.texto}", mensajes.incidencia(juez.Incidencia(False, "precios", f"{a.pieza}: {a.texto}")))
    else:
        primera = pd.Timestamp(config["primera_senyal"])
        piezas = papel.piezas_de(cierres)
        hasta = min(hoy, papel.ultimo_dia_completo(cierres))
        reales = [s for s in papel.senyales_reales(piezas, hasta) if s >= primera]
        tratada = pd.Timestamp(estado["ultima_senyal_tratada"]) if estado.get("ultima_senyal_tratada") else None
        for s in reales:  # la IA en sombra, una vez por senyal (si el bot no corrio ese dia, la siguiente vuelta)
            if tratada is not None and s <= tratada:
                continue
            mes = papel.revision(cierres, s, primera)
            desde = s - timedelta(days=35)
            titulares = noticias.del_periodo(base / "noticias.csv", desde.tz_localize(precios.MADRID).to_pydatetime(), ahora)
            r = dep.preguntar_ia(mes, titulares, set(mes["compras"]), token=dep.secretos.claude_token)
            ia.apuntar(base / "ia_diario.jsonl", s.to_pydatetime(), mes, r, ahora)
            estado["ultima_senyal_tratada"] = s.date().isoformat()
            estado["ia"] = {"senyal": s.date().isoformat(), "ok": r.ok, "explicacion": r.explicacion,
                            "motivo": r.motivo, "frenos": [list(x) for x in r.frenos]}
            for pieza, motivo in r.frenos:
                aviso(f"freno:{s.date()}:{pieza}", mensajes.freno_ia(pieza, motivo))
            if not r.ok:
                aviso(f"ia:{s.date()}", mensajes.incidencia(juez.Incidencia(False, "ia", r.motivo)))
            estado["pendiente_resumen"] = s.date().isoformat()
        try:
            p = papel.calcular(cierres, primera, hasta)
        except ValueError:
            p = None  # la primera senyal aun no se ha ejecutado
        if p is not None:
            ayer = pd.Timestamp(estado["papel_hasta"]) if estado.get("papel_hasta") else None
            nuevas = papel.nuevas(p, ayer)
            if nuevas:
                for fecha in sorted({o.fecha for o in nuevas}):
                    ops = [o for o in nuevas if o.fecha == fecha]
                    aviso(f"ops:{fecha.date()}", mensajes.operaciones(ops, p))
            if estado.get("pendiente_resumen") and p.ultima_senyal is not None and \
                    p.ultima_senyal >= pd.Timestamp(estado["pendiente_resumen"]) and p.hasta > p.ultima_senyal:
                proxima = (p.hasta + pd.offsets.BMonthEnd(1)) if p.hasta == p.hasta + pd.offsets.BMonthEnd(0) \
                    else p.hasta + pd.offsets.BMonthEnd(0)
                aviso(f"resumen:{estado['pendiente_resumen']}", mensajes.resumen_mensual(
                    p, (estado.get("ia") or {}).get("explicacion") or None, proxima))
                estado["pendiente_resumen"] = None
            incid = juez.juzgar(p, config["huella"], huella(), reales, dias_con_vuelta(base) | {hoy}, avisos_precios)
            semana = f"{hoy.isocalendar().year}-{hoy.isocalendar().week}"
            for i in incid:  # las que duran (caida, huella, coherencia), como mucho una vez por semana
                clave = i.texto if i.tipo in ("precios", "senyal_sin_vuelta") else semana
                aviso(f"inc:{i.tipo}:{clave}", mensajes.incidencia(i))
            if ahora.weekday() == 6:
                aviso(f"todo_bien:{hoy.isocalendar().year}-{hoy.isocalendar().week}", mensajes.todo_bien(p))
            if ahora.month == 4:
                aviso(f"renta:{ahora.year}", f"{mensajes.CABECERA}\nRecordatorio de la renta: el papel no tiene "
                                             "dinero real, no hay nada que declarar por Ebisu.")
            estado.update({"papel_hasta": p.hasta.date().isoformat(), "valor_eur": p.valor_eur,
                           "si_vende_hoy_eur": p.si_vende_hoy_eur, "caida": p.caida, "referencia_eur": p.referencia_eur,
                           "pesos": p.pesos, "puntos": p.puntos,
                           "ultima_senyal": p.ultima_senyal.date().isoformat() if p.ultima_senyal is not None else None,
                           "operaciones": [{"fecha": o.fecha.date().isoformat(), "pieza": o.pieza, "antes": o.antes,
                                            "despues": o.despues} for o in p.operaciones],
                           "incidencias": [{"grave": i.grave, "tipo": i.tipo, "texto": i.texto} for i in incid]})
        else:
            for a in avisos_precios:
                aviso(f"precios:{a.tipo}:{a.pieza}:{a.texto}", mensajes.incidencia(juez.Incidencia(False, "precios", f"{a.pieza}: {a.texto}")))
    estado["titulares_nuevos"] = n_titulares
    estado["ia_version"] = dep.comprobar_ia(dep.secretos.claude_token)  # salud del panel; no gasta cuota
    _escribir_json(base / "estado.json", estado)
    mandar = dep.mandar or (lambda t: telegram.enviar(dep.secretos.telegram_token, dep.secretos.telegram_chat_id, t).ok)
    enviados, descartados = cola.enviar_pendientes(f_cola, mandar, ahora)
    apuntar_vuelta(base, ahora, True, f"avisos nuevos {len(apuntados)}, enviados {enviados}, descartados {descartados}")
    estado["latido"] = dep.latido_ok(dep.secretos.healthcheck)
    _escribir_json(base / "estado.json", estado)
    try:  # el panel, lo ultimo (ya con el latido) y sin poder tumbar la vuelta: si falla, se avisa manyana
        panel.escribir(base, ahora)
    except Exception as exc:
        cola.apuntar(f_cola, f"panel:{hoy.date()}",
                     mensajes.incidencia(juez.Incidencia(False, "panel", f"{type(exc).__name__}")), ahora)
    return estado


def principal(ahora: datetime, base: Path = VAR, dep: Dependencias | None = None) -> int:
    """La vuelta sin caerse en silencio: si revienta, latido de fallo y un aviso directo."""
    dep = dep or Dependencias()
    try:
        vuelta(ahora, base, dep)
        return 0
    except Exception as exc:
        detalle = secretos.tapar(f"{type(exc).__name__}: {exc}", *dep.secretos.todos())
        log.error("la vuelta fallo: %s\n%s", detalle, secretos.tapar(traceback.format_exc(), *dep.secretos.todos()))
        try:
            apuntar_vuelta(base, ahora, False, detalle)
        except OSError:
            pass
        dep.latido_fallo(dep.secretos.healthcheck)
        mandar = dep.mandar or (lambda t: telegram.enviar(dep.secretos.telegram_token, dep.secretos.telegram_chat_id, t).ok)
        mandar(mensajes.incidencia(juez.Incidencia(True, "bot", f"la vuelta del dia fallo: {detalle}")))
        return 1


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--seco", action="store_true")
    ap.add_argument("--empezar", metavar="AAAA-MM-DD")
    a = ap.parse_args()
    ahora = datetime.now(precios.MADRID)
    if a.empezar:
        print(empezar(VAR, a.empezar))
        return
    if a.seco:
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            if (VAR / "papel.json").exists():
                (base / "papel.json").write_text((VAR / "papel.json").read_text(encoding="utf-8"), encoding="utf-8")
            dep = Dependencias(mandar=lambda t: True, latido_ok=lambda u: None, latido_fallo=lambda u: None,
                               preguntar_ia=lambda *a, **k: ia.Respuesta(False, "seco: la IA no se llama"))
            estado = vuelta(ahora, base, dep)
            avisos = json.loads((base / "cola.json").read_text(encoding="utf-8"))["enviados"] if (base / "cola.json").exists() else []
        print(f"SECO: OK. Empezado: {estado['empezado']}; avisos que habria mandado: {len(avisos)}; "
              f"titulares: {estado['titulares_nuevos']}. Nada guardado ni enviado.")
        return
    sys.exit(principal(ahora))


if __name__ == "__main__":
    main()
