"""Validacion del simulador de E2 ANTES de medir (docs/diseno-estudio-2.md, seccion 6, paso 3). Datos INVENTADOS.

Uso: .venv/Scripts/python.exe estudios/estudio2/validar2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulador2 import BANDA, TIPO, VENTANA_VOL, pesos_objetivo, referencia2, simular2, sinteticos  # noqa: E402

FALLOS: list[str] = []


def comprobar(nombre: str, obtenido: float, esperado: float, tol: float = 1e-10) -> None:
    ok = abs(obtenido - esperado) <= tol
    print(f"{'OK   ' if ok else 'FALLA'} {nombre}: obtenido {obtenido:.12f}, esperado {esperado:.12f}")
    if not ok:
        FALLOS.append(nombre)


def main() -> None:
    precio, total, rep, mon = sinteticos()
    ini, fin = str(precio.index[0].date()), str(precio.index[-1].date())

    # 1. Todo en un activo desde el primer dia, sin costes: exactamente comprar y mantener (impuesto al final).
    r = simular2(precio, total, rep, mon, ini, fin, coste=0.0, calendario={ini: {"a0": 1.0}})
    ref = referencia2(precio["a0"], ini, fin)
    comprobar("1. comprar y mantener: bolsillo", r.bolsillo, ref.bolsillo)
    comprobar("1. comprar y mantener: peor diferencia diaria", float((r.valor - ref.valor).abs().max()), 0.0)

    # 2. Pesos: con precios que solo suben, las 4 medias se superan y los pesos son las partes por riesgo (suman 1),
    #    inversas a la desviacion de los ultimos 63 dias (calculada aqui a mano).
    f = pd.bdate_range("2013-01-01", periods=400)
    rng = np.random.default_rng(1)
    sube = pd.DataFrame({f"a{i}": 100 * np.cumprod(1 + 0.001 + np.abs(rng.normal(0, 0.002 * (i + 1), 400)))
                         for i in range(3)}, index=f)
    w = pesos_objetivo(sube, f[-1])
    s = sube.pct_change().iloc[-VENTANA_VOL:].std(ddof=1)
    a_mano = (1 / s) / (1 / s).sum()
    comprobar("2. pesos: suman 1 con todo en tendencia", float(w.sum()), 1.0)
    comprobar("2. pesos: inversos al riesgo (peor diferencia)", float((w - a_mano).abs().max()), 0.0)
    comprobar("2. sin historia suficiente: nada", float(pesos_objetivo(sube, f[150]) is None), 1.0)

    # 3. Banda de 2 puntos: de 50 % a 51,5 % no se toca; a 53 % si; salir del todo desde un 1 %, siempre.
    d = [str(x.date()) for x in precio.index[[0, 10, 20, 30, 40]]]
    cal = {d[0]: {"a0": 0.50, "a1": 0.01}, d[1]: {"a0": 0.515, "a1": 0.01}, d[2]: {"a0": 0.53, "a1": 0.01},
           d[3]: {"a0": 0.53, "a1": 0.0}}
    r = simular2(precio, total, rep, mon, ini, fin, coste=0.0, calendario=cal)
    pw = r.pesos
    comprobar("3. banda: el dia 10 no se toca a0 (no llega al 51,5 %)", float(abs(pw.loc[d[1], "a0"] - 0.515) > 1e-6), 1.0)
    comprobar("3. banda: el dia 20 a0 pasa a 53 %", float(pw.loc[d[2], "a0"]), 0.53, 1e-9)
    comprobar("3. banda: el dia 30 a1 sale del todo aunque solo era un 1 %", float(pw.loc[d[3], "a1"]), 0.0)
    comprobar("3. la banda es de 2 puntos", BANDA, 0.02)

    # 4. Repartos: 1 euro por participacion un dia, con todo invertido: tributa el 19 % al cobrarlo.
    rep4 = rep.copy()
    dia = precio.index[100]
    rep4.loc[dia, "a0"] = 1.0
    r = simular2(precio, total, rep4, mon, ini, fin, coste=0.0, calendario={ini: {"a0": 1.0}})
    unidades = 1.0 / precio["a0"].iloc[0]
    sin = simular2(precio, total, rep, mon, ini, fin, coste=0.0, calendario={ini: {"a0": 1.0}})
    # A mano: el reparto paga el 19 % al cobrarse; el neto crece en el monetario y su ganancia paga el 19 % al final.
    neto_rep = unidades * 1.0 * (1 - TIPO)
    ganancia_mon = neto_rep * (mon.loc[precio.index[-1]] / mon.loc[dia] - 1)
    comprobar("4. reparto: impuestos de mas (al cobrar y su ganancia en el monetario)", r.impuestos - sin.impuestos,
              TIPO * unidades * 1.0 + TIPO * ganancia_mon, 1e-12)
    comprobar("4. reparto: el neto entra en el monetario el mismo dia",
              float(r.valor.loc[dia] - sin.valor.loc[dia]), unidades * (1 - TIPO), 1e-9)

    # 5. Con la senyal real y costes: nunca apalancamiento (pesos <= 100 %, valor > 0).
    r = simular2(precio, total, rep, mon, str(precio.index[260].date()), fin)
    comprobar("5. pesos invertidos nunca por encima del 100 %", float((r.pesos.sum(axis=1) <= 1 + 1e-9).all()), 1.0)
    comprobar("5. valor siempre positivo", float((r.valor > 0).all()), 1.0)
    comprobar("5. hay operaciones", float(r.operaciones > 0), 1.0)

    print()
    print("VALIDACION E2:", "TODO OK" if not FALLOS else f"FALLAN {len(FALLOS)}: {', '.join(FALLOS)}")
    sys.exit(1 if FALLOS else 0)


if __name__ == "__main__":
    main()
