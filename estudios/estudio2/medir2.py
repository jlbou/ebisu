"""Medicion del estudio 2 con una sola orden (docs/diseno-estudio-2.md): E2 y H1-F en la reserva, una vez.

  --ensayo                  todo el camino con datos INVENTADOS (no mide nada real)
  --reserva --confirmo      mide la RESERVA (2015-2026) con las dos candidatas y escribe el veredicto del juez

Cada candidata pasa con: 1) gana a su referencia o casi la iguala con claramente menos caida; 2) no pierde;
3) Sharpe probabilistico contra 0 >= 0,95. Se niega si ya hay veredicto o sin --confirmo.
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
from juez import metricas, pasa, sharpe_deflactado  # noqa: E402
from simulador import referencia, simular  # noqa: E402
from simulador2 import referencia2, simular2, sinteticos  # noqa: E402

from medir import VARIANTES as VARIANTES_E1  # noqa: E402

RAIZ = AQUI.parents[1]
DATOS = RAIZ / "var" / "estudio2"
PIEZAS_E1 = RAIZ / "var" / "estudio1" / "piezas_eur.csv"
VEREDICTO = RAIZ / "docs" / "estudios" / "estudio2-reserva.md"
RESERVA = ("2015-01-01", "2026-09-30")
LISTON_PSR = 0.95
ACTIVOS = ["bolsa_eeuu", "bolsa_europa", "bolsa_emergente", "bonos_euro_estado", "bonos_euro_corp",
           "bonos_eeuu_estado", "oro", "materias_primas", "inmobiliario"]


def monetario_bce(fechas: pd.DatetimeIndex) -> pd.Series:
    """Indice del monetario en euros (EONIA hasta 09/2019, STR desde 10/2019), dias naturales / 360."""
    e1 = RAIZ / "var" / "estudio1"
    eonia = pd.read_csv(e1 / "bce_eonia.csv", index_col=0, parse_dates=True)["valor"]
    estr = pd.read_csv(e1 / "bce_estr.csv", index_col=0, parse_dates=True)["valor"]
    corte = pd.Timestamp("2019-10-01")
    tipo = pd.concat([eonia[eonia.index < corte], estr[estr.index >= corte]])
    t = tipo.reindex(tipo.index.union(fechas)).sort_index().ffill().reindex(fechas).shift(1).fillna(0)
    dias = fechas.to_series().diff().dt.days.fillna(0).to_numpy()
    return pd.Series(np.cumprod(1 + t.to_numpy() / 100 * dias / 360), index=fechas)


def cargar() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    ref = pd.read_csv(DATOS / "referencia.csv", index_col=0, parse_dates=True)
    cal = ref.index
    precio, total, rep = {}, {}, {}
    for a in ACTIVOS:
        d = pd.read_csv(DATOS / f"{a}.csv", index_col=0, parse_dates=True)
        precio[a] = d["Close"].reindex(cal).ffill()
        total[a] = d["Adj Close"].reindex(cal).ffill()
        div = d["Dividends"] if "Dividends" in d else pd.Series(0.0, index=d.index)
        rep[a] = div.reindex(cal).fillna(0.0)  # un reparto en un dia sin sesion en Xetra se pierde: no pasa (ver bajar.py)
    return (pd.DataFrame(precio), pd.DataFrame(total), pd.DataFrame(rep), monetario_bce(cal), ref["Adj Close"])


def juzgar(nombre: str, valor: pd.Series, bolsillo: float, mon: pd.Series, ref_valor: pd.Series, ref_bolsillo: float,
           ops: int) -> dict:
    m = metricas(valor, bolsillo, mon)
    mr = metricas(ref_valor, ref_bolsillo, mon)
    psr = sharpe_deflactado(m, 0.0, 1)  # una sola prueba: es el Sharpe probabilistico contra 0
    cond = pasa(m, mr, None)
    cond["3. exceso sobre el monetario con confianza >= 0,95"] = psr >= LISTON_PSR
    return {"nombre": nombre, "m": m, "ref": mr, "psr": psr, "ops": ops, "condiciones": cond,
            "pasa": all(cond.values())}


def dos_x(valor: pd.Series, mon: pd.Series) -> dict:
    r = valor.pct_change().fillna(0)
    rm = mon.reindex(valor.index).pct_change().fillna(0)
    v2 = (1 + 2 * r - rm).cumprod()
    anyos = (v2.index[-1] - v2.index[0]).total_seconds() / 86400 / 365.25
    return {"tae": float(v2.iloc[-1] ** (1 / anyos) - 1), "caida": float((1 - v2 / v2.cummax()).max())}


def medir(precio, total, rep, mon, ref_precio, piezas_e1, ini, fin) -> list[dict]:
    out = []
    r = simular2(precio, total, rep, mon, ini, fin)
    rf = referencia2(ref_precio, ini, fin)
    j = juzgar("E2", r.valor, r.bolsillo, mon, rf.valor, rf.bolsillo, r.operaciones)
    j["dos_x"] = dos_x(r.valor, mon)
    out.append(j)
    h1f = next(v for v in VARIANTES_E1 if v.nombre == "H1-F")
    r1 = simular(piezas_e1, h1f, ini, fin)
    rf1 = referencia(piezas_e1, ini, fin)
    j1 = juzgar("H1-F", r1.valor, r1.bolsillo, piezas_e1["monetario"], rf1.valor, rf1.bolsillo, r1.operaciones)
    j1["dos_x"] = dos_x(r1.valor, piezas_e1["monetario"])
    out.append(j1)
    return out


def informe(res: list[dict], ensayo: bool) -> str:
    ini, fin = RESERVA
    lin = [f"# Estudio 2: veredicto de la RESERVA ({ini} a {fin})" + (" - ENSAYO CON DATOS INVENTADOS" if ensayo else ""),
           "", "Generado por `estudios/estudio2/medir2.py` con el criterio de `docs/diseno-estudio-2.md`. Una sola vez,",
           "sin retoques. Cada candidata con su referencia (E2: MSCI World en euros; H1-F: la del estudio 1).", "",
           "| Candidata | TAE neta | Caida max. | Sharpe | Confianza (>= 0,95) | Operaciones | Referencia: TAE / caida | Pasa |",
           "|---|---|---|---|---|---|---|---|"]
    for j in res:
        m, r = j["m"], j["ref"]
        lin.append(f"| {j['nombre']} | {m.tae:.2%} | {m.caida:.1%} | {m.sharpe:.2f} | {j['psr']:.3f} | {j['ops']} | "
                   f"{r.tae:.2%} / {r.caida:.1%} | {'SI' if j['pasa'] else 'no'} |")
    lin += ["", "Condiciones:", ""]
    for j in res:
        lin.append(f"- **{j['nombre']}**: " + "; ".join(f"{k}: {'si' if v else 'NO'}" for k, v in j["condiciones"].items()))
    pasan = [j["nombre"] for j in res if j["pasa"]]
    ver = ("PASAN LAS DOS: van al papel en paralelo" if len(pasan) == 2 else
           f"PASA {pasan[0]}: va al papel" if pasan else "NO PASA NINGUNA: Ebisu se cierra con el indexado mantenido")
    lin += ["", f"**Veredicto: {ver}.**", "", "Informacion que no decide (doble exposicion, antes de impuestos):", ""]
    for j in res:
        lin.append(f"- {j['nombre']}: TAE {j['dos_x']['tae']:.2%}, caida {j['dos_x']['caida']:.1%}")
    return "\n".join(lin) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ensayo", action="store_true")
    ap.add_argument("--reserva", action="store_true")
    ap.add_argument("--confirmo", action="store_true")
    a = ap.parse_args()
    if a.ensayo:
        precio, total, rep, mon = sinteticos(dias=3600, n=9)
        precio.columns = total.columns = rep.columns = ACTIVOS
        rng = np.random.default_rng(2)
        f = precio.index
        piezas = pd.DataFrame({k: 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, len(f)))) for k in ("bolsa", "bonos", "oro")},
                              index=f)
        piezas["monetario"] = mon.to_numpy()
        ini, fin = str(f[300].date()), str(f[-1].date())
        res = medir(precio, total, rep, mon, precio["bolsa_eeuu"], piezas, ini, fin)
        print(informe(res, ensayo=True))
        ok = len(res) == 2 and all("pasa" in j for j in res)
        print("ENSAYO E2:", "OK (dos candidatas juzgadas, veredicto solo en pantalla)" if ok else "FALLA")
        sys.exit(0 if ok else 1)
    if not (a.reserva and a.confirmo):
        sys.exit("Para medir: --reserva --confirmo (una sola vez). Para probar: --ensayo.")
    if VEREDICTO.exists():
        sys.exit(f"Ya hay un veredicto de la reserva ({VEREDICTO.name}): no se vuelve a medir.")
    precio, total, rep, mon, ref = cargar()
    piezas = pd.read_csv(PIEZAS_E1, index_col=0, parse_dates=True)
    res = medir(precio, total, rep, mon, ref, piezas, *RESERVA)
    VEREDICTO.write_text(informe(res, ensayo=False), encoding="utf-8")
    print(VEREDICTO.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
