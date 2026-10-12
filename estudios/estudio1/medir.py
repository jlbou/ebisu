"""Medicion del estudio 1 con una sola orden (docs/diseno-estudio-1.md, secciones 3-7).

  --ensayo                         todo el camino con datos INVENTADOS (no mide nada real); para validar
  --exploracion --confirmo         mide la EXPLORACION (2001-2014) con las 5 variantes y escribe el veredicto del juez
  --reserva --confirmo             mide la RESERVA (2015-2026) UNA vez, solo con la ganadora de la exploracion
  --ensayo-reserva                 el camino de la reserva con datos INVENTADOS

Antes de medir de verdad se niega si: faltan ficheros de divisas, ya existe un veredicto de la exploracion, o no se
pasa --confirmo. Nada se retoca despues de ver el resultado.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h2 import PARES, ResultadoH2, dias_de_par, simular_h2  # noqa: E402
from juez import N_VARIANTES, metricas, pasa, pasa_h2, sharpe_deflactado  # noqa: E402
from simulador import Variante, referencia, simular  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
PIEZAS = RAIZ / "var" / "estudio1" / "piezas_eur.csv"
VEREDICTO = RAIZ / "docs" / "estudios" / "estudio1-exploracion.md"
GANADORA = RAIZ / "docs" / "estudios" / "estudio1-exploracion.json"
VEREDICTO_RESERVA = RAIZ / "docs" / "estudios" / "estudio1-reserva.md"
RESERVA = ("2015-01-01", "2026-09-30")
EXPLORACION = ("2001-07-01", "2014-12-31")

# Gasto anual extra = el del ETF o fondo real - el que ya lleva la serie larga (aprox. el actual de cada fondo de
# Vanguard: VTSMX 0,14 %, VGTSX 0,17 %, VBMFX 0,15 %; el oro y el monetario no llevan). Nunca negativo (conservador).
LARGA_BOLSA = 0.6 * 0.0014 + 0.4 * 0.0017
GASTO_ETF = {"bolsa": max(0.0019 - LARGA_BOLSA, 0), "bonos": max(0.0010 - 0.0015, 0), "oro": 0.0025,
             "monetario": 0.0010}
GASTO_FONDOS = {"bolsa": max(0.0015 - LARGA_BOLSA, 0), "bonos": max(0.0015 - 0.0015, 0), "monetario": 0.0015}

VARIANTES = [
    Variante("H1-M", frecuencia="M", gasto_extra=GASTO_ETF),
    Variante("H1-S", frecuencia="S", gasto_extra=GASTO_ETF),
    Variante("H1-MB", frecuencia="M", escalonada=False, gasto_extra=GASTO_ETF),
    Variante("H1-F", frecuencia="M", fondos=True, piezas=("bolsa", "bonos"), coste_lado=0.0, retraso=6,
             gasto_extra=GASTO_FONDOS),
]


def dos_x(valor: pd.Series, monetario: pd.Series) -> dict:
    """Informacion (no decide): doble exposicion pagando el monetario por lo prestado, antes de impuestos."""
    r = valor.pct_change().fillna(0)
    rm = monetario.reindex(valor.index).pct_change().fillna(0)
    v2 = (1 + 2 * r - rm).cumprod()
    anyos = (v2.index[-1] - v2.index[0]).total_seconds() / 86400 / 365.25
    return {"tae_antes_de_impuestos": float(v2.iloc[-1] ** (1 / anyos) - 1),
            "caida": float((1 - v2 / v2.cummax()).max())}


def medir(piezas: pd.DataFrame, dias_fx: dict[str, pd.DataFrame], ini: str, fin: str) -> dict:
    mon = piezas["monetario"]
    filas, series = {}, {}
    ref = referencia(piezas, ini, fin)
    m_ref = metricas(ref.valor, ref.bolsillo, mon)
    for v in VARIANTES:
        r = simular(piezas, v, ini, fin)
        filas[v.nombre] = {"m": metricas(r.valor, r.bolsillo, mon), "ref": m_ref, "ops": r.operaciones,
                           "impuestos": r.impuestos, "costes": r.costes, "dos_x": dos_x(r.valor, mon)}
        series[v.nombre] = r.valor

    # H2: desde que hay datos de los siete pares (mas un dia, para tener el de ayer), hasta el fin de la exploracion.
    ini_h2 = max(ini, str(max(d.index.min() for d in dias_fx.values()).date()))
    dias = sorted(set().union(*(d.index for d in dias_fx.values())))
    mon_fx = mon.reindex(mon.index.union(pd.DatetimeIndex(dias))).ffill().reindex(pd.DatetimeIndex(dias))
    h2: ResultadoH2 = simular_h2(dias_fx, mon_fx, ini_h2, fin)
    ref_h2 = referencia(piezas, ini_h2, fin)
    filas["H2"] = {"m": metricas(h2.valor, h2.bolsillo, mon_fx), "ref": metricas(ref_h2.valor, ref_h2.bolsillo, mon),
                   "ops": int(sum(len(o) for o in h2.por_operacion.values())), "impuestos": h2.impuestos,
                   "costes": float("nan"), "dos_x": None, "h2": pasa_h2(h2.por_operacion)}

    var_sr = float(np.var([f["m"].sharpe_diario for f in filas.values()], ddof=1))
    for f in filas.values():
        f["dsr"] = sharpe_deflactado(f["m"], var_sr, N_VARIANTES)
        f["condiciones"] = {**pasa(f["m"], f["ref"], f["dsr"]), **f.get("h2", {})}
        f["pasa"] = all(f["condiciones"].values())
    pasan = [n for n, f in filas.items() if f["pasa"]]
    ganadora = max(pasan, key=lambda n: filas[n]["dsr"]) if pasan else None
    return {"tramo": (ini, fin), "inicio_h2": ini_h2, "var_sr": var_sr, "filas": filas, "ganadora": ganadora}


def medir_reserva(piezas: pd.DataFrame, dias_fx: dict[str, pd.DataFrame], ganadora: str) -> dict:
    """Solo la ganadora, solo condiciones 1 y 2 (el deflactado ya se exigio en la exploracion)."""
    ini, fin = RESERVA
    mon = piezas["monetario"]
    ref = referencia(piezas, ini, fin)
    m_ref = metricas(ref.valor, ref.bolsillo, mon)
    if ganadora == "H2":
        dias = sorted(set().union(*(d.index for d in dias_fx.values())))
        mon_fx = mon.reindex(mon.index.union(pd.DatetimeIndex(dias))).ffill().reindex(pd.DatetimeIndex(dias))
        r = simular_h2(dias_fx, mon_fx, ini, fin)
        m = metricas(r.valor, r.bolsillo, mon_fx)
        ops = int(sum(len(o) for o in r.por_operacion.values()))
    else:
        v = next(x for x in VARIANTES if x.nombre == ganadora)
        r = simular(piezas, v, ini, fin)
        m = metricas(r.valor, r.bolsillo, mon)
        ops = r.operaciones
    cond = pasa(m, m_ref, None)
    return {"ganadora": ganadora, "m": m, "ref": m_ref, "ops": ops, "condiciones": cond, "pasa": all(cond.values())}


def informe_reserva(res: dict, ensayo: bool) -> str:
    m, r = res["m"], res["ref"]
    ini, fin = RESERVA
    lin = [f"# Estudio 1: veredicto de la RESERVA ({ini} a {fin})" + (" - ENSAYO CON DATOS INVENTADOS" if ensayo else ""),
           "", f"Solo {res['ganadora']}, la ganadora de la exploracion. Se mira una sola vez. Sin retoques.", "",
           "| Variante | TAE neta | Caida max. | Sharpe | Operaciones | Referencia: TAE / caida |", "|---|---|---|---|---|---|",
           f"| {res['ganadora']} | {m.tae:.2%} | {m.caida:.1%} | {m.sharpe:.2f} | {res['ops']} | {r.tae:.2%} / {r.caida:.1%} |",
           "", "; ".join(f"{k}: {'si' if v else 'NO'}" for k, v in res["condiciones"].items()), "",
           f"**Veredicto: {'PASA: va al papel hacia adelante' if res['pasa'] else 'NO PASA: la conclusion es el indexado mantenido'}.**"]
    return chr(10).join(lin) + chr(10)


def informe(res: dict, ensayo: bool) -> str:
    ini, fin = res["tramo"]
    lin = [f"# Estudio 1: veredicto de la EXPLORACION ({ini} a {fin})" + (" - ENSAYO CON DATOS INVENTADOS" if ensayo else ""),
           "", "Generado por `estudios/estudio1/medir.py` con el criterio de `docs/diseno-estudio-1.md`. Sin retoques.",
           f"H2 empieza el {res['inicio_h2']} (cuando hay datos de los siete pares).", "",
           "| Variante | TAE neta | Caida max. | Sharpe | Deflactado | Operaciones | Referencia: TAE / caida | Pasa |",
           "|---|---|---|---|---|---|---|---|"]
    for n, f in res["filas"].items():
        m, r = f["m"], f["ref"]
        lin.append(f"| {n} | {m.tae:.2%} | {m.caida:.1%} | {m.sharpe:.2f} | {f['dsr']:.3f} | {f['ops']} | "
                   f"{r.tae:.2%} / {r.caida:.1%} | {'SI' if f['pasa'] else 'no'} |")
    lin += ["", "Condiciones de cada variante:", ""]
    for n, f in res["filas"].items():
        lin.append(f"- **{n}**: " + "; ".join(f"{k}: {'si' if v else 'NO'}" for k, v in f["condiciones"].items()))
    lin += ["", f"**Veredicto: {'va a la reserva ' + res['ganadora'] if res['ganadora'] else 'NO PASA NINGUNA: la conclusion es el indexado mantenido; la reserva queda sin tocar'}.**",
            "", "Informacion que no decide (doble exposicion, antes de impuestos):", ""]
    for n, f in res["filas"].items():
        if f["dos_x"]:
            lin.append(f"- {n}: TAE {f['dos_x']['tae_antes_de_impuestos']:.2%}, caida {f['dos_x']['caida']:.1%}")
    return "\n".join(lin) + "\n"


def datos_inventados(hasta: str = "2014-12-31") -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(11)
    f = pd.bdate_range("2000-08-30", hasta)
    piezas = pd.DataFrame({a: 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, len(f)))) for a in ("bolsa", "bonos", "oro")},
                          index=f)
    piezas["monetario"] = 100 * np.cumprod(np.full(len(f), 1.00008))
    fx = {}
    for p in PARES:
        c = 1 + np.cumsum(rng.normal(0, 0.005, len(f)))
        rango = np.abs(rng.normal(0, 0.004, len(f)))
        d = pd.DataFrame({"bid_o": c, "bid_h": c + rango, "bid_l": c - rango, "bid_c": c + rng.normal(0, 0.002, len(f))},
                         index=f)
        for k in ("o", "h", "l", "c"):
            d[f"ask_{k}"] = d[f"bid_{k}"] + 0.0002
        fx[p] = d.loc["2003-05-05":]
    return piezas, fx


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ensayo", action="store_true")
    ap.add_argument("--exploracion", action="store_true")
    ap.add_argument("--confirmo", action="store_true")
    ap.add_argument("--reserva", action="store_true")
    ap.add_argument("--ensayo-reserva", action="store_true")
    a = ap.parse_args()
    if a.ensayo_reserva:
        piezas, fx = datos_inventados(hasta="2026-09-30")
        for g in ("H1-M", "H2"):
            res = medir_reserva(piezas, {p: d.loc["2014-10-01":] for p, d in fx.items()}, g)
            print(informe_reserva(res, ensayo=True))
        print("ENSAYO DE LA RESERVA: OK (una variante, condiciones 1 y 2, veredicto solo en pantalla)")
        sys.exit(0)
    if a.reserva:
        if not a.confirmo:
            sys.exit("Para medir la reserva: --reserva --confirmo (una sola vez).")
        if not GANADORA.exists():
            sys.exit("No hay veredicto de la exploracion: primero --exploracion --confirmo.")
        if VEREDICTO_RESERVA.exists():
            sys.exit(f"Ya hay un veredicto de la reserva ({VEREDICTO_RESERVA.name}): no se vuelve a medir.")
        ganadora = json.loads(GANADORA.read_text(encoding="utf-8"))["ganadora"]
        if not ganadora:
            sys.exit("En la exploracion no paso ninguna: la reserva queda sin tocar (indexado mantenido).")
        piezas = pd.read_csv(PIEZAS, index_col=0, parse_dates=True)
        try:
            fx = {p: dias_de_par(p) for p in PARES} if ganadora == "H2" else {}
        except ValueError as exc:
            sys.exit(f"No se mide: {exc}")
        res = medir_reserva(piezas, fx, ganadora)
        VEREDICTO_RESERVA.write_text(informe_reserva(res, ensayo=False), encoding="utf-8")
        print(VEREDICTO_RESERVA.read_text(encoding="utf-8"))
        sys.exit(0)
    if a.ensayo:
        piezas, fx = datos_inventados()
        res = medir(piezas, fx, *EXPLORACION)
        texto = informe(res, ensayo=True)
        print(texto)
        ok = len(res["filas"]) == N_VARIANTES and all("pasa" in f for f in res["filas"].values())
        print("ENSAYO:", "OK (5 variantes juzgadas, veredicto escrito solo en pantalla)" if ok else "FALLA")
        sys.exit(0 if ok else 1)
    if not (a.exploracion and a.confirmo):
        sys.exit("Para medir: --exploracion --confirmo (una sola vez). Para probar: --ensayo.")
    if VEREDICTO.exists():
        sys.exit(f"Ya hay un veredicto de la exploracion ({VEREDICTO.name}): no se vuelve a medir.")
    piezas = pd.read_csv(PIEZAS, index_col=0, parse_dates=True)
    try:
        fx = {p: dias_de_par(p) for p in PARES}
    except ValueError as exc:
        sys.exit(f"No se mide: {exc}")
    res = medir(piezas, fx, *EXPLORACION)
    VEREDICTO.write_text(informe(res, ensayo=False), encoding="utf-8")
    GANADORA.write_text(json.dumps({"ganadora": res["ganadora"], "tramo": res["tramo"]}), encoding="utf-8")
    print(VEREDICTO.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
