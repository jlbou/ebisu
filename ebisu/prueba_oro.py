"""Prueba de oro con precios REALES (docs/plan-bot-papel.md 10, B1): el papel del bot sobre los cierres de Yahoo tiene
que dar exactamente lo mismo que el simulador del estudio 4 (`estudios/estudio4/simulador4.py`) con esos cierres.

Baja los precios a un fichero temporal (no toca el del papel). Solo ensenya si coincide, no cifras de rendimiento.

    .venv/Scripts/python.exe -m ebisu.prueba_oro [--senyal 2026-06-30]
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd

from ebisu import papel as P
from ebisu import precios as PR

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "estudios" / "estudio4"))
import simulador4 as S  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--senyal", default="2026-06-30", help="primera senyal (ultimo dia habil de un mes)")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as d:
        cierres, avisos = PR.actualizar(Path(d) / "precios.csv", datetime.now(PR.MADRID))
    hasta = cierres.dropna().index[-1]
    papel = P.calcular(cierres, pd.Timestamp(a.senyal), hasta)
    piezas = P.piezas_de(cierres).loc[:hasta]
    inicio = P.dia_de_ejecucion(piezas, pd.Timestamp(a.senyal))
    r = S.simular(piezas, S.Variante("H1-M"), str(inicio.date()), str(hasta.date()))
    checks = {
        "valor diario identico": papel.valor.equals(r.valor),
        "lo que queda si vende hoy identico": abs(papel.si_vende_hoy_eur - P.CAPITAL_EUR * r.bolsillo) < 1e-9,
        "operaciones contadas = las de la estrategia": len(papel.operaciones) == r.operaciones,
    }
    print(f"Precios reales hasta {hasta:%d/%m/%Y}; papel desde {inicio:%d/%m/%Y}; {len(papel.operaciones)} operaciones; "
          f"avisos de precios: {len(avisos)}")
    for k, ok in checks.items():
        print(f"{'OK   ' if ok else 'FALLA'} {k}")
    sys.exit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
