"""Diagnostico del estudio 3 (docs/plan-estudio-3.md, seccion 4): puerta 1, con los 7 pares principales (ya vistos).

  --validar                 casos calculados a mano con datos INVENTADOS
  --ensayo                  todo el camino con datos INVENTADOS (no mide nada real)
  --medir --confirmo        mide el diagnostico UNA vez y escribe docs/estudios/estudio3-diagnostico.md

Barreras provisionales del diagnostico: objetivo en la mitad del rango de ayer, stop de 1 rango medio, maximo 5 dias.
El veto de eventos NO se aplica aqui: los eventos son uno de los escenarios que se marcan.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "estudio1"))
import simulador3 as s3  # noqa: E402

RAIZ = AQUI.parents[1]
PARES = ["EURUSD", "USDJPY", "GBPUSD", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
VEREDICTO = RAIZ / "docs" / "estudios" / "estudio3-diagnostico.md"
BARRERAS = s3.Barreras(k_stop=1.0, max_dias=5)
ESCENARIOS = ["evento", "tendencia", "volatilidad", "miedo", "rotura"]
FALLOS: list[str] = []


def comprobar(nombre: str, obtenido, esperado, tol: float = 1e-12) -> None:
    if isinstance(esperado, (bool, str)) or esperado is None:
        ok = obtenido == esperado
    else:
        ok = abs(obtenido - esperado) <= tol
    print(f"{'OK   ' if ok else 'FALLA'} {nombre}: obtenido {obtenido}, esperado {esperado}")
    if not ok:
        FALLOS.append(nombre)


# ---------------------------------------------------------------------------------------------------------------------
# Datos inventados
# ---------------------------------------------------------------------------------------------------------------------

def dias_laborables(desde: str, n: int) -> list[pd.Timestamp]:
    return list(pd.bdate_range(desde, periods=n))


def velas(dias: list[pd.Timestamp], cambios: dict | None = None, spread: float = 0.0001,
          planos: set | None = None) -> pd.DataFrame:
    """Cada dia: 24 velas de 1 hora de 17:00 (dia anterior) a 17:00 de Nueva York, planas a 1,0000 (bid), salvo a las
    10:00 (maximo 1,0050) y a las 12:00 (minimo 0,9950): rango de 0,0100. cambios: {(dia, hora_ny): {campo: valor}};
    planos: dias sin esos picos (para que nada toque el objetivo)."""
    filas, idx = [], []
    for d in dias:
        inicio = (d - pd.Timedelta(days=1)).replace(hour=17).tz_localize(s3.NY)
        for k in range(24):
            ts = inicio + pd.Timedelta(hours=k)
            o = h_ = l_ = c = 1.0
            if ts.hour == 10 and d not in (planos or set()):
                h_ = 1.0050
            if ts.hour == 12 and d not in (planos or set()):
                l_ = 0.9950
            fila = {"bid_o": o, "bid_h": h_, "bid_l": l_, "bid_c": c}
            for clave, v in ((cambios or {}).get((d, ts.hour), {})).items():
                fila[clave] = v
            for x in ("o", "h", "l", "c"):
                fila[f"ask_{x}"] = fila[f"bid_{x}"] + spread
            for clave, v in ((cambios or {}).get((d, ts.hour), {})).items():
                if clave.startswith("ask_"):
                    fila[clave] = v
            filas.append(fila)
            idx.append(ts.tz_convert("UTC"))
    return s3.preparar_horas(pd.DataFrame(filas, index=pd.DatetimeIndex(idx)))


def tipos_fijos(base: float = 2.0, cot: float = 1.0) -> pd.DataFrame:
    dias = pd.date_range("2000-01-01", "2030-01-01", freq="D")  # diario: preparar_tipos no arrastra mas de 31 dias
    return s3.preparar_tipos(pd.DataFrame({"EUR": base, "USD": cot}, index=dias))


def validar() -> None:
    tipos = tipos_fijos()
    noche_compra = (2.0 - 1.0 - s3.RECARGO) / 100 / 365
    neto = lambda bruto, noches: bruto - 2 * s3.COMISION + noches - s3.CONVERSION * abs(bruto)  # noqa: E731

    # Dia normal: rango 0,9951 (ask) a 1,0050 (bid). Objetivo = mitad del rango medio = (1,00505 + 0,99505) / 2.
    objetivo = (1.00505 + 0.99505) / 2
    # A. Martes: a las 3:00 el ask baja a 0,9945 (cruza 1 pip el 0,9951 de ayer): compra a 0,9951; a las 5:00 el bid
    #    toca 1,0005 >= objetivo: vende al objetivo. Mismo dia: sin intereses.
    dias = dias_laborables("2024-01-08", 26)  # 26 laborables: el 26 es martes
    t = dias[-1]
    h = velas(dias, {(t, 3): {"ask_l": 0.9945}, (t, 5): {"bid_h": 1.0005}})
    ops = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5))
    comprobar("A: una operacion", len(ops), 1)
    o = ops.iloc[0]
    comprobar("A: compra", int(o["sentido"]), 1)
    comprobar("A: entra al minimo de ayer", o["entrada"], 0.9951, 1e-12)
    comprobar("A: sale al objetivo", o["salida"], objetivo, 1e-12)
    comprobar("A: motivo", o["motivo"], "objetivo")
    bruto = (objetivo - 0.9951) / 0.9951
    comprobar("A: neto (sin noches)", o["neto"], neto(bruto, 0.0), 1e-15)

    # B. Stop: a las 6:00 el bid baja a 0,9840 (stop = 0,9951 - 0,0100 = 0,9851): se ejecuta 1 diferencial peor.
    h = velas(dias, {(t, 3): {"ask_l": 0.9945}, (t, 6): {"bid_l": 0.9840}})
    o = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5)).iloc[0]
    comprobar("B: motivo", o["motivo"], "stop")
    comprobar("B: sale al stop menos un diferencial", o["salida"], 0.9851 - 0.0001, 1e-12)

    # C. En la misma hora se tocan stop y objetivo: cuenta el stop.
    h = velas(dias, {(t, 3): {"ask_l": 0.9945}, (t, 6): {"bid_l": 0.9840, "bid_h": 1.0010}})
    o = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5)).iloc[0]
    comprobar("C: stop y objetivo a la vez -> stop", o["motivo"], "stop")

    # D. La hora abre ya por debajo del stop: se ejecuta a la apertura.
    h = velas(dias, {(t, 3): {"ask_l": 0.9945}, (t, 6): {"bid_o": 0.9800, "bid_l": 0.9790}})
    o = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5)).iloc[0]
    comprobar("D: salto -> a la apertura", o["salida"], 0.9800, 1e-12)

    # E. Limite de tiempo de 2 dias: compra el lunes, nada mas pasa; sale el miercoles al cierre de las 15:00 (bid
    #    1,0000). Noches: lunes->martes y martes->miercoles (la del miercoles, triple, es despues de salir). Los dias
    #    desde la entrada son planos (sin los picos de las 10:00 y las 12:00) para que no se toque el objetivo.
    dias_e = dias_laborables("2024-01-08", 30)  # termina el viernes 16/02; el lunes de entrada es el 12/02
    lunes = [d for d in dias_e if d.dayofweek == 0][-1]
    todos = dias_e + dias_laborables(dias_e[-1] + pd.Timedelta(days=1), 3)
    h = velas(todos, {(lunes, 3): {"ask_l": 0.9945}}, planos={d for d in todos if d >= lunes})
    o = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 2)).iloc[0]
    comprobar("E: dia de entrada (lunes)", o["dia"].dayofweek, 0)
    comprobar("E: motivo", o["motivo"], "tiempo")
    comprobar("E: sale el miercoles", o["hora_salida"].tz_convert(s3.NY).dayofweek, 2)
    comprobar("E: dos noches de intereses", o["intereses"], 2 * noche_compra, 1e-15)

    # F. Viernes: compra el jueves; el viernes a las 15:00 se cierra (una noche, la del jueves).
    jueves = [d for d in dias_e if d.dayofweek == 3][-1]
    h = velas(todos, {(jueves, 3): {"ask_l": 0.9945}}, planos={d for d in todos if d >= jueves})
    o = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5)).iloc[0]
    comprobar("F: motivo", o["motivo"], "viernes")
    comprobar("F: una noche", o["intereses"], noche_compra, 1e-15)

    # G. La caida solo ocurre a las 16:00 de Nueva York: no se abre (T3).
    h = velas(dias, {(t, 16): {"ask_l": 0.9945}})
    comprobar("G: 16:00-18:00 sin operaciones", len(s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5))), 0)

    # H. Venta espejo: a las 3:00 el bid sube a 1,0056 (cruza 1 pip el 1,0050 de ayer): vende a 1,0050; a las 5:00
    #    el ask toca 0,9998 <= objetivo: compra al objetivo.
    h = velas(dias, {(t, 3): {"bid_h": 1.0056}, (t, 5): {"ask_l": 0.9998}})
    o = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5)).iloc[0]
    comprobar("H: venta", int(o["sentido"]), -1)
    comprobar("H: entra al maximo de ayer", o["entrada"], 1.0050, 1e-12)
    comprobar("H: bruto", o["bruto"], (1.0050 - objetivo) / 1.0050, 1e-15)

    # I. 26 de diciembre: no se abre (T3).
    dias_n = dias_laborables("2023-11-15", 30)
    dic = [d for d in dias_n if d.month == 12 and d.day == 26][0]
    h = velas(dias_n, {(dic, 3): {"ask_l": 0.9945}})
    comprobar("I: 24/12-2/1 sin operaciones", len(s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5))), 0)

    # J. Intereses: la noche del miercoles cuenta triple (compra el martes, limite 2 dias -> sale el jueves).
    martes = [d for d in dias_e if d.dayofweek == 1][-1]
    h = velas(todos, {(martes, 3): {"ask_l": 0.9945}}, planos={d for d in todos if d >= martes})
    o = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 2)).iloc[0]
    comprobar("J: martes->miercoles (1) + miercoles->jueves (3)", o["intereses"], 4 * noche_compra, 1e-15)

    # K. Escenarios: evento el dia de entrada, volatilidad (ayer, rango 3 veces el medio), rotura del minimo de 20.
    lunes_v = dias[-2]
    h = velas(dias, {(t, 3): {"ask_l": 0.9945}, (t, 5): {"bid_h": 1.0005},
                     (lunes_v, 10): {"bid_h": 1.0200}, (lunes_v, 12): {"bid_l": 0.9950}})
    ops = s3.operaciones(h, "EURUSD", tipos, s3.Barreras(1.0, 5))
    eventos = pd.DataFrame({"fecha": [t.date().isoformat()], "divisa": ["EUR"], "evento": ["BCE"]})
    vix = pd.Series(np.r_[np.full(250, 15.0), 40.0], index=pd.bdate_range(end=t - pd.Timedelta(days=1), periods=251))
    m = s3.marcar(ops, s3.dias_de_horas(h), h, eventos, vix, "EURUSD")
    m = m[m["dia"] == t].iloc[0]  # el pico de ayer tambien da una venta ese dia: se mira la compra del dia t
    comprobar("K: evento", bool(m["evento"]), True)
    comprobar("K: volatilidad (rango de ayer 0,0250 > 2 x 0,0100)", bool(m["volatilidad"]), True)
    comprobar("K: miedo (VIX de ayer, el mas alto del anyo)", bool(m["miedo"]), True)
    comprobar("K: rotura del minimo de 20 dias", bool(m["rotura"]), True)
    comprobar("K: tendencia (sin 200 dias de historia: no)", bool(m["tendencia"]), False)

    # L. Juez: 10 operaciones; 6 no marcadas con media +0,001; las 2 peores (5 %: la peor) marcadas.
    ops = pd.DataFrame({"neto": [0.002, 0.0, 0.001, 0.001, 0.002, 0.0, -0.01, -0.02, 0.003, 0.004],
                        "marcada": [False] * 6 + [True] * 4})
    j = s3.juzgar(ops)
    comprobar("L: media no marcadas", j["media_no_marcadas"], 0.001, 1e-15)
    comprobar("L: parte no marcadas", j["parte_no_marcadas"], 0.6, 1e-15)
    comprobar("L: pasa", j["pasa"], True)


# ---------------------------------------------------------------------------------------------------------------------
# Medicion
# ---------------------------------------------------------------------------------------------------------------------

def horas_dukascopy(par: str) -> pd.DataFrame:
    sys.path.insert(0, str(AQUI.parent / "h2reserva"))
    from h2_horas import horas_de_par
    h = horas_de_par(par).drop(columns=["dia"])
    return s3.preparar_horas(h)


def diagnosticar(horas: dict[str, pd.DataFrame], tipos: pd.DataFrame, eventos: pd.DataFrame,
                 vix: pd.Series) -> pd.DataFrame:
    todas = []
    for par, h in horas.items():
        ops = s3.operaciones(h, par, tipos, BARRERAS)
        if len(ops):
            todas.append(s3.marcar(ops, s3.dias_de_horas(h), h, eventos, vix, par))
        print(f"{par}: {len(ops)} operaciones", flush=True)
    return pd.concat(todas, ignore_index=True)


def informe(ops: pd.DataFrame, ensayo: bool) -> str:
    j = s3.juzgar(ops)
    lin = ["# Estudio 3: diagnostico (puerta 1)" + (" - ENSAYO CON DATOS INVENTADOS" if ensayo else ""), "",
           "Generado por `estudios/estudio3/diagnostico.py` con el criterio de `docs/plan-estudio-3.md` (seccion 4).",
           "Los 7 pares principales, 2003-2026 (ya vistos): solo dice si vale la pena seguir. Barreras provisionales:",
           "objetivo en la mitad del rango de ayer, stop de 1 rango medio, maximo 5 dias. Resultado neto por operacion",
           "(fraccion del nominal, sin apalancamiento ni impuestos).", "",
           f"Operaciones: {j['operaciones']} (compras {int((ops['sentido'] == 1).sum())}, "
           f"ventas {int((ops['sentido'] == -1).sum())}); media de todas: {j['media_todas']:+.4%}.", "",
           "| | Valor | Necesario | Cumple |", "|---|---|---|---|",
           f"| Media de las no marcadas | {j['media_no_marcadas']:+.4%} (mediana {j['mediana_no_marcadas']:+.4%}) | > 0 "
           f"| {'si' if j['condiciones']['1. las no marcadas ganan de media'] else 'NO'} |",
           f"| Parte no marcada | {j['parte_no_marcadas']:.1%} | >= 40 % "
           f"| {'si' if j['condiciones']['2. quedan al menos el 40 %'] else 'NO'} |",
           f"| Peores (5 %) marcadas | {j['peores_marcadas']:.1%} | >= 50 % "
           f"| {'si' if j['condiciones']['3. las marcadas tienen al menos la mitad de las peores'] else 'NO'} |", "",
           "Por escenario (una operacion puede tener varios):", "",
           "| Escenario | Operaciones | Media | Parte de la perdida total |", "|---|---|---|---|"]
    perdida = ops.loc[ops["neto"] < 0, "neto"].sum()
    for e in ESCENARIOS:
        x = ops[ops[e]]
        lin.append(f"| {e} | {len(x)} | {x['neto'].mean():+.4%} | {x.loc[x['neto'] < 0, 'neto'].sum() / perdida:.1%} |")
    x = ops[~ops["marcada"]]
    lin.append(f"| ninguno | {len(x)} | {x['neto'].mean():+.4%} | {x.loc[x['neto'] < 0, 'neto'].sum() / perdida:.1%} |")
    lin += ["", "Informacion (no decide): por sentido y por par, media de las no marcadas.", "",
            "| | Operaciones no marcadas | Media |", "|---|---|---|"]
    for nombre, x in [("compras", ops[(ops["sentido"] == 1) & ~ops["marcada"]]),
                      ("ventas", ops[(ops["sentido"] == -1) & ~ops["marcada"]])] + \
            [(p, ops[(ops["par"] == p) & ~ops["marcada"]]) for p in sorted(ops["par"].unique())]:
        lin.append(f"| {nombre} | {len(x)} | {x['neto'].mean():+.4%} |")
    lin += ["", "Motivos de salida: " + ", ".join(f"{k} {v}" for k, v in ops["motivo"].value_counts().items()) + ".",
            "", f"**Veredicto: {'PASA la puerta: vale la pena seguir' if j['pasa'] else 'NO PASA la puerta: se para'}.**"]
    return "\n".join(lin) + "\n"


def ensayo() -> None:
    rng = np.random.default_rng(3)
    dias = dias_laborables("2019-01-01", 320)
    horas = {}
    for par in ("EURUSD", "AUDUSD"):
        base = velas(dias)
        ruido = np.cumsum(rng.normal(0, 0.0008, len(base)))
        for c in ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"):
            base[c] = base[c] + ruido
        base["bid_h"] += np.abs(rng.normal(0, 0.0006, len(base)))
        base["ask_h"] = base["bid_h"] + 0.0001
        base["bid_l"] -= np.abs(rng.normal(0, 0.0006, len(base)))
        base["ask_l"] = base["bid_l"] + 0.0001
        horas[par] = base
    tipos = s3.preparar_tipos(pd.DataFrame({"EUR": 1.0, "USD": 2.0, "AUD": 3.0},
                                           index=pd.date_range("2000-01-01", "2030-01-01", freq="D")))
    eventos = pd.DataFrame({"fecha": [d.date().isoformat() for d in dias[::15]], "divisa": "USD", "evento": "Fed"})
    vix = pd.Series(rng.normal(18, 5, 600), index=pd.bdate_range(end=dias[-1], periods=600))
    ops = diagnosticar(horas, tipos, eventos, vix)
    print(informe(ops, ensayo=True))
    print("ENSAYO DIAGNOSTICO:", "OK" if len(ops) > 20 else "FALLA")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--ensayo", action="store_true")
    ap.add_argument("--medir", action="store_true")
    ap.add_argument("--confirmo", action="store_true")
    a = ap.parse_args()
    if a.validar:
        validar()
        print("VALIDACION:", "OK" if not FALLOS else f"FALLA ({', '.join(FALLOS)})")
        sys.exit(1 if FALLOS else 0)
    if a.ensayo:
        ensayo()
        sys.exit(0)
    if not (a.medir and a.confirmo):
        sys.exit("Para medir: --medir --confirmo (una sola vez). Para probar: --validar o --ensayo.")
    if VEREDICTO.exists():
        sys.exit(f"Ya hay un diagnostico ({VEREDICTO.name}): no se vuelve a medir.")
    datos = RAIZ / "var" / "estudio3"
    tipos = s3.preparar_tipos(pd.read_csv(datos / "tipos.csv", index_col=0, parse_dates=True))
    vix = pd.read_csv(datos / "vix.csv", index_col=0, parse_dates=True)["vix"]
    eventos = pd.read_csv(AQUI / "eventos.csv")
    horas = {p: horas_dukascopy(p) for p in PARES}
    ops = diagnosticar(horas, tipos, eventos, vix)
    ops.to_csv(datos / "diagnostico_operaciones.csv", index=False)
    VEREDICTO.write_text(informe(ops, ensayo=False), encoding="utf-8")
    print(VEREDICTO.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
