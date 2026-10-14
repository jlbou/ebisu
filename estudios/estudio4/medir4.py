"""Medicion del estudio 4 con una sola orden (docs/plan-estudio-4.md 4-7).

  --ensayo             todo el camino con datos INVENTADOS (no lee var/, no mide nada real)
  --seco              corre todo con los datos REALES pero no ensenya ni guarda ningun numero (solo que no falla)
  --medir --confirmo   mide UNA vez 1971-2026 (y 1990-2026) y escribe docs/estudios/estudio4-veredicto.md

Se niega a medir si ya existe el veredicto o falta --confirmo. Nada se retoca despues de ver el resultado.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import juez4 as J  # noqa: E402
import modelo4 as M  # noqa: E402
from simulador4 import Variante, dias_de_senyal, referencia, simular  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
PIEZAS = RAIZ / "var" / "estudio4" / "piezas_eur.csv"
VEREDICTO = RAIZ / "docs" / "estudios" / "estudio4-veredicto.md"
TOTAL, RECIENTE, LIMPIO = ("1971-01-01", "2026-09-30"), ("1990-01-01", "2026-09-30"), ("1971-01-01", "2000-12-31")

# Gasto anual de los vehiculos reales (las series largas son indices sin gastos): bolsa como VWCE/EUNL, bonos como el
# ETF del Tesoro cubierto (0,10 %), oro y monetario como en el estudio 1; fondos, 0,15 %.
GASTO_ETF = {"bolsa": 0.0019, "bonos": 0.0010, "oro": 0.0025, "monetario": 0.0010}
GASTO_FONDOS = {"bolsa": 0.0015, "bonos": 0.0015, "monetario": 0.0015}
BASES = [
    Variante("H1-M", gasto_extra=GASTO_ETF),
    Variante("H1-F", fondos=True, piezas=("bolsa", "bonos"), coste_lado=0.0, retraso=6, gasto_extra=GASTO_FONDOS),
    Variante("H1-M + volatilidad", gasto_extra=GASTO_ETF, capa2=True),
    Variante("H1-M + fiscal", gasto_extra=GASTO_ETF, capa3=True),
]


def correr(piezas: pd.DataFrame, v: Variante, tramo: tuple[str, str]) -> dict:
    con = simular(piezas, v, *tramo)
    sin = simular(piezas, replace(v, impuestos=False), *tramo)
    return {"con": con, "sin": sin, "m": J.metricas(con.valor, con.bolsillo, sin.valor, piezas["monetario"])}


def correr_ref(piezas: pd.DataFrame, tramo: tuple[str, str]) -> dict:
    con, sin = referencia(piezas, *tramo), referencia(piezas, *tramo, impuestos=False)
    return {"con": con, "sin": sin, "m": J.metricas(con.valor, con.bolsillo, sin.valor, piezas["monetario"])}


def medir(piezas: pd.DataFrame, datos_modelo: tuple, cpi: pd.Series) -> dict:
    ref = {k: correr_ref(piezas, t) for k, t in (("total", TOTAL), ("reciente", RECIENTE), ("limpio", LIMPIO))}
    ref_anual = J.anuales(ref["total"]["sin"].valor)
    tipos = J.tipos_de_mercado(ref_anual, J.inflacion_anual(cpi))
    filas = {}
    for v in BASES:
        filas[v.nombre] = {"v": v, **{k: correr(piezas, v, t) for k, t in (("total", TOTAL), ("reciente", RECIENTE),
                                                                           ("limpio", LIMPIO))}}
    mejor = max(BASES, key=lambda v: filas[v.nombre]["total"]["m"].sharpe)
    dias = dias_de_senyal(piezas.index)
    anyos = range(int(TOTAL[0][:4]) - 1, int(TOTAL[1][:4]) + 1)
    mult, imp_max = M.multiplicador(piezas["bolsa_usd"], dias, anyos, *datos_modelo)
    v5 = replace(mejor, nombre=f"{mejor.nombre} + modelo", multiplicador=mult)
    filas[v5.nombre] = {"v": v5, **{k: correr(piezas, v5, t) for k, t in (("total", TOTAL), ("reciente", RECIENTE),
                                                                         ("limpio", LIMPIO))}}
    mon = piezas["monetario"]
    pbo = J.pbo_dos(J.exceso_mensual(filas[mejor.nombre]["total"]["sin"].valor, mon),
                    J.exceso_mensual(filas[v5.nombre]["total"]["sin"].valor, mon))
    var_sr = J.varianza_liston([f["total"]["m"].sharpe_mensual for f in filas.values()],
                               filas[mejor.nombre]["total"]["m"].meses)
    for nombre, f in filas.items():
        f["dsr"] = J.sharpe_deflactado(f["total"]["m"], var_sr)
        f["tipos"] = J.condicion_tipos(J.anuales(f["total"]["sin"].valor), ref_anual, tipos)
        cond = {"1. 1971-2026": J.condicion_total(f["total"]["m"], ref["total"]["m"]),
                "2. 1990-2026": J.condicion_total(f["reciente"]["m"], ref["reciente"]["m"]),
                "3. tipos de mercado": all(p for _, _, p in f["tipos"].values()),
                "4. no es suerte (deflactado >= 0,95)": f["dsr"] >= J.LISTON_DSR}
        if nombre == v5.nombre:
            cond["5a. PBO < 0,5"] = pbo < 0.5
            cond["5b. ninguna variable > 40 %"] = imp_max <= 0.40
            cond["5c. mejora el Sharpe de su base"] = f["total"]["m"].sharpe > filas[mejor.nombre]["total"]["m"].sharpe
        f["condiciones"] = cond
        f["pasa"] = all(cond.values())
        f["info_limpio"] = J.condicion_total(f["limpio"]["m"], ref["limpio"]["m"])
    pasan = sorted((n for n, f in filas.items() if f["pasa"]), key=lambda n: -filas[n]["dsr"])
    ganadora = None
    if pasan:
        ganadora = pasan[0]
        cerca = [n for n in pasan if filas[pasan[0]]["dsr"] - filas[n]["dsr"] < 0.02 and not filas[n]["v"].fondos]
        if filas[ganadora]["v"].fondos and cerca:
            ganadora = cerca[0]
    return {"ref": ref, "tipos": tipos, "filas": filas, "mejor": mejor.nombre, "pbo": pbo, "imp_max": imp_max,
            "var_sr": var_sr, "ganadora": ganadora}


def informe(res: dict, ensayo: bool) -> str:
    r = res["ref"]
    lin = ["# Estudio 4: veredicto (1971-2026 y 1990-2026)" + (" - ENSAYO CON DATOS INVENTADOS" if ensayo else ""), "",
           "Generado por `estudios/estudio4/medir4.py` con el criterio de `docs/plan-estudio-4.md`. Una vez, sin retoques.",
           "", "| Variante | TAE 1971-2026 | Caida | Sharpe | Deflactado | TAE 1990-2026 | Caida | Pasa |",
           "|---|---|---|---|---|---|---|---|",
           f"| Referencia (bolsa mantenida) | {r['total']['m'].tae:.2%} | {r['total']['m'].caida:.1%} | "
           f"{r['total']['m'].sharpe:.2f} | - | {r['reciente']['m'].tae:.2%} | {r['reciente']['m'].caida:.1%} | - |"]
    for n, f in res["filas"].items():
        t, c = f["total"]["m"], f["reciente"]["m"]
        lin.append(f"| {n} | {t.tae:.2%} | {t.caida:.1%} | {t.sharpe:.2f} | {f['dsr']:.3f} | {c.tae:.2%} | "
                   f"{c.caida:.1%} | {'SI' if f['pasa'] else 'no'} |")
    lin += ["", "Condiciones:", ""]
    for n, f in res["filas"].items():
        lin.append(f"- **{n}**: " + "; ".join(f"{k}: {'si' if v else 'NO'}" for k, v in f["condiciones"].items()))
    lin += ["", "Tipos de mercado (media anual de estrategia - referencia, antes de impuestos):", "",
            "| Variante | " + " | ".join(f"{t} ({len(a)} anyos)" for t, a in res["tipos"].items()) + " |",
            "|---|" + "---|" * len(res["tipos"])]
    for n, f in res["filas"].items():
        lin.append(f"| {n} | " + " | ".join(f"{d:+.1%} {'si' if p else 'NO'}" for _, d, p in f["tipos"].values()) + " |")
    lin += ["", f"Modelo: base = {res['mejor']}; PBO = {res['pbo']:.2f}; variable mas importante = {res['imp_max']:.0%}.",
            f"Liston: N = {J.N_INTENTOS}, varianza de los Sharpe mensuales = {res['var_sr']:.6f}.", "",
            f"**Veredicto: {'PASA ' + res['ganadora'] + ': va al papel' if res['ganadora'] else 'NO PASA NINGUNA'}.**",
            "", "Solo informacion (no decide): condicion 1 en 1971-2000 (tramo limpio): "
            + "; ".join(f"{n}: {'si' if f['info_limpio'] else 'no'}" for n, f in res["filas"].items()),
            "", "Anacronismos: ETF antes de 1993, traspasos antes de 2003 y la ley de hoy; tramos en euros de hoy sobre "
            "250 € de 1971; oro de 1999-2000 con medias mensuales; bolsa solo de EE. UU. hasta 1996."]
    return "\n".join(lin) + "\n"


def info_extra() -> list[str]:
    """Solo informacion (plan 7), con datos reales: no decide nada ni se usa para elegir."""
    import montar as mt

    lin = []
    r_us = mt.french_diario()
    f = r_us.index[(r_us.index >= "1926-07-01") & (r_us.index <= "1970-12-31")]
    us = (1 + r_us.reindex(f)).cumprod()
    rf = pd.read_csv(mt.F / "french_diario" / "F-F_Research_Data_Factors_daily.csv", skiprows=4, index_col=0)
    rf = rf[rf.index.astype(str).str.fullmatch(r"\d{8}")]["RF"].astype(float) / 100
    rf.index = pd.to_datetime(rf.index.astype(str))
    piezas = pd.DataFrame({"bolsa": us, "monetario": (1 + rf.reindex(f).fillna(0)).cumprod()})
    v = Variante("H1 bolsa EE. UU.", piezas=("bolsa",), impuestos=False)
    s = simular(piezas, v, "1927-07-01", "1970-12-31").valor
    h = piezas["bolsa"].loc["1927-07-01":]
    for n, x in (("H1 sobre la bolsa de EE. UU.", s), ("bolsa de EE. UU. mantenida", h)):
        lin.append(f"- 1927-1970, {n} (dolares, antes de impuestos): TAE {J.tae(x.iloc[-1] / x.iloc[0], x):.2%}, "
                   f"caida {J.caida(x):.1%}")
    fi = mt.french_internacional()
    fi = fi[(fi.index >= "1975-01-01") & (fi.index <= "1996-12-31")]
    nivel = (1 + fi).cumprod()
    dentro = (nivel > nivel.rolling(10).mean()).shift(1).fillna(False)
    regla = (1 + np.where(dentro, fi, 0.0)).cumprod()
    regla = pd.Series(regla, index=fi.index)
    for n, x in (("media de 10 meses", regla), ("mantenida", nivel)):
        lin.append(f"- 1975-1996, bolsa fuera de EE. UU. {n} (mensual, dolares, sin el monetario): TAE "
                   f"{J.tae(x.iloc[-1] / x.iloc[0], x):.2%}, caida {J.caida(x):.1%}")
    return lin


def datos_inventados() -> tuple[pd.DataFrame, tuple, pd.Series]:
    rng = np.random.default_rng(4)
    f = pd.bdate_range("1969-07-01", "2026-09-30")
    piezas = pd.DataFrame({a: np.exp(np.cumsum(rng.normal(0.0002, 0.01, len(f)))) for a in ("bolsa", "bonos", "oro")},
                          index=f)
    piezas["monetario"] = np.cumprod(np.full(len(f), 1.0001))
    piezas["bolsa_usd"] = piezas["bolsa"] * np.exp(np.cumsum(rng.normal(0, 0.003, len(f))))
    meses = pd.date_range("1926-07-31", "2026-09-30", freq="ME")
    sec = pd.DataFrame(rng.normal(0.008, 0.05, (len(meses), 6)), index=meses, columns=[f"S{i}" for i in range(6)])
    rf = pd.Series(0.003, index=meses)
    infl = pd.Series(rng.normal(0.03, 0.02, len(meses)), index=meses)
    cpi = pd.Series(np.cumprod(1 + rng.normal(0.003, 0.003, len(meses))), index=meses)
    return piezas, (sec, rf, infl), cpi


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ensayo", action="store_true")
    ap.add_argument("--medir", action="store_true")
    ap.add_argument("--confirmo", action="store_true")
    ap.add_argument("--seco", action="store_true")
    a = ap.parse_args()
    if a.ensayo:
        piezas, dm, cpi = datos_inventados()
        res = medir(piezas, dm, cpi)
        print(informe(res, ensayo=True))
        ok = len(res["filas"]) == 5 and all("pasa" in f for f in res["filas"].values())
        print("ENSAYO:", "OK (5 variantes juzgadas, veredicto solo en pantalla)" if ok else "FALLA")
        sys.exit(0 if ok else 1)
    if a.seco:
        piezas = pd.read_csv(PIEZAS, index_col=0, parse_dates=True)
        cpi = pd.read_csv(M.F / "fred_CPIAUCSL.csv", index_col=0, parse_dates=True).iloc[:, 0].astype(float)
        res = medir(piezas, (M.sectores(), M.letras_mensuales(), M.inflacion()), cpi)
        informe(res, ensayo=False)
        info_extra()
        print(f"SECO: OK, sin errores con los datos reales ({len(res['filas'])} variantes; nada ensenyado ni guardado)")
        sys.exit(0)
    if not (a.medir and a.confirmo):
        sys.exit("Para medir: --medir --confirmo (una sola vez). Para probar: --ensayo.")
    if VEREDICTO.exists():
        sys.exit(f"Ya hay un veredicto ({VEREDICTO.name}): no se vuelve a medir.")
    piezas = pd.read_csv(PIEZAS, index_col=0, parse_dates=True)
    cpi = pd.read_csv(M.F / "fred_CPIAUCSL.csv", index_col=0, parse_dates=True).iloc[:, 0].astype(float)
    res = medir(piezas, (M.sectores(), M.letras_mensuales(), M.inflacion()), cpi)
    texto = informe(res, ensayo=False) + "\nMas informacion (no decide):\n\n" + "\n".join(info_extra()) + "\n"
    VEREDICTO.write_text(texto, encoding="utf-8")
    print(VEREDICTO.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
