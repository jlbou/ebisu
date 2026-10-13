"""H2 en la reserva de divisas (docs/diseno-h2-reserva.md): una sola medicion, 2015-2026.

  --ensayo                  todo el camino con datos INVENTADOS (no mide nada real)
  --reserva --confirmo      mide la RESERVA de divisas una vez y escribe el veredicto

Se niega si ya hay veredicto o sin --confirmo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "estudio1"))
from h2 import PARES, dias_de_par, simular_h2  # noqa: E402
from juez import metricas, pasa, pasa_h2, sharpe_deflactado  # noqa: E402
from medir import datos_inventados  # noqa: E402
from simulador import referencia  # noqa: E402

RAIZ = AQUI.parents[1]
PIEZAS = RAIZ / "var" / "estudio1" / "piezas_eur.csv"
VEREDICTO = RAIZ / "docs" / "estudios" / "h2-reserva.md"
RESERVA = ("2015-01-01", "2026-09-30")
LISTON_PSR = 0.99


def medir(piezas: pd.DataFrame, dias_fx: dict[str, pd.DataFrame], ini: str, fin: str) -> dict:
    mon = piezas["monetario"]
    dias = sorted(set().union(*(d.index for d in dias_fx.values())))
    mon_fx = mon.reindex(mon.index.union(pd.DatetimeIndex(dias))).ffill().reindex(pd.DatetimeIndex(dias))
    r = simular_h2(dias_fx, mon_fx, ini, fin)
    m = metricas(r.valor, r.bolsillo, mon_fx)
    ref = referencia(piezas, ini, fin)
    mr = metricas(ref.valor, ref.bolsillo, mon)
    psr = sharpe_deflactado(m, 0.0, 1)  # una sola prueba: Sharpe probabilistico contra 0
    cond = pasa(m, mr, None)
    cond["3. exceso sobre el monetario con confianza >= 0,99"] = psr >= LISTON_PSR
    cond.update(pasa_h2(r.por_operacion))
    medias = {p: float(v.mean()) for p, v in r.por_operacion.items()}
    return {"m": m, "ref": mr, "psr": psr, "ops": int(sum(len(o) for o in r.por_operacion.values())),
            "medias": medias, "condiciones": cond, "pasa": all(cond.values())}


def informe(res: dict, ensayo: bool) -> str:
    ini, fin = RESERVA
    m, r = res["m"], res["ref"]
    lin = [f"# H2: veredicto de la RESERVA de divisas ({ini} a {fin})" + (" - ENSAYO CON DATOS INVENTADOS" if ensayo else ""),
           "", "Generado por `estudios/h2reserva/medir_h2.py` con el criterio de `docs/diseno-h2-reserva.md`. Una sola",
           "vez, sin retoques.", "",
           "| Variante | TAE neta | Caida max. | Sharpe | Confianza (>= 0,99) | Operaciones | Referencia: TAE / caida | Pasa |",
           "|---|---|---|---|---|---|---|---|",
           f"| H2 | {m.tae:.2%} | {m.caida:.1%} | {m.sharpe:.2f} | {res['psr']:.3f} | {res['ops']} | "
           f"{r.tae:.2%} / {r.caida:.1%} | {'SI' if res['pasa'] else 'no'} |", "", "Condiciones:", ""]
    lin += [f"- {k}: {'si' if v else 'NO'}" for k, v in res["condiciones"].items()]
    lin += ["", "Resultado medio por operacion y par (informacion):", ""]
    lin += [f"- {p}: {v:+.4%}" for p, v in res["medias"].items()]
    ver = "PASA: decide el propietario (decision 5 y si se puede operar sin CFD)" if res["pasa"] else \
        "NO PASA: H2 queda descartada del todo"
    return "\n".join(lin + ["", f"**Veredicto: {ver}.**"]) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ensayo", action="store_true")
    ap.add_argument("--reserva", action="store_true")
    ap.add_argument("--confirmo", action="store_true")
    a = ap.parse_args()
    if a.ensayo:
        piezas, fx = datos_inventados(hasta="2026-09-30")
        res = medir(piezas, {p: d.loc["2014-10-01":] for p, d in fx.items()}, *RESERVA)
        print(informe(res, ensayo=True))
        ok = "pasa" in res and len(res["medias"]) == len(PARES)
        print("ENSAYO H2 RESERVA:", "OK (veredicto solo en pantalla)" if ok else "FALLA")
        sys.exit(0 if ok else 1)
    if not (a.reserva and a.confirmo):
        sys.exit("Para medir: --reserva --confirmo (una sola vez). Para probar: --ensayo.")
    if VEREDICTO.exists():
        sys.exit(f"Ya hay un veredicto ({VEREDICTO.name}): no se vuelve a medir.")
    piezas = pd.read_csv(PIEZAS, index_col=0, parse_dates=True)
    try:
        fx = {p: dias_de_par(p) for p in PARES}
    except ValueError as exc:
        sys.exit(f"No se mide: {exc}")
    res = medir(piezas, fx, *RESERVA)
    VEREDICTO.write_text(informe(res, ensayo=False), encoding="utf-8")
    print(VEREDICTO.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
