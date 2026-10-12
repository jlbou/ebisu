"""Contraste de las divisas de Dukascopy con una segunda fuente oficial (docs/diseno-estudio-1.md, H2 y seccion 2).

Segunda fuente: el tipo de referencia del BCE (14:15 de Frankfurt, dentro del dia de 17:00 a 17:00 de Nueva York de
la misma fecha). Para cada par se calcula el cruce (p. ej. USD/JPY = yenes por euro / dolares por euro) y se mira si
cae dentro del rango del dia de Dukascopy (minimo de compra a maximo de venta). Regla de la seccion 2: si queda fuera
mas de un 0,5 % algun dia sin explicacion, se para y se decide.

NO calcula rendimientos. Uso: .venv/Scripts/python.exe estudios/estudio1/contraste_h2.py [PAR ...]
"""

from __future__ import annotations

import csv
import io
import sys
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h2 import DUKAS, PARES, dias_de_par  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CACHE = RAIZ / "var" / "estudio1" / "bce_divisas"
API = "https://data-api.ecb.europa.eu/service/data/EXR/D.{m}.EUR.SP00.A?format=csvdata&startPeriod=2003-01-01"
UMBRAL = 0.005


def bce(moneda: str) -> pd.Series:
    """Unidades de la moneda por euro, tipo de referencia del BCE (se guarda en var/ para no pedirlo otra vez)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{moneda}.csv"
    if not f.exists():
        pet = urllib.request.Request(API.format(m=moneda), headers={"User-Agent": "ebisu-estudio"})
        with urllib.request.urlopen(pet, timeout=120) as r:
            filas = [(x["TIME_PERIOD"], x["OBS_VALUE"]) for x in csv.DictReader(io.StringIO(r.read().decode()))
                     if x.get("OBS_VALUE")]
        pd.DataFrame(filas, columns=["fecha", "valor"]).to_csv(f, index=False)
    s = pd.read_csv(f, index_col=0, parse_dates=True)["valor"].astype(float)
    return s


def oficial(par: str) -> pd.Series:
    base, cotiza = par[:3], par[3:]
    por_euro = {m: (pd.Series(1.0, index=bce("USD").index) if m == "EUR" else bce(m)) for m in (base, cotiza)}
    return (por_euro[cotiza] / por_euro[base]).dropna()


def contrastar(par: str) -> dict:
    d = dias_de_par(par)
    ref = oficial(par).reindex(d.index).dropna()
    lo, hi = d["bid_l"].reindex(ref.index), d["ask_h"].reindex(ref.index)
    fuera = pd.concat([(lo - ref) / ref, (ref - hi) / ref], axis=1).max(axis=1).clip(lower=0)
    malos = fuera[fuera > UMBRAL]
    return {"par": par, "dias": len(ref), "desde": ref.index.min().date(), "hasta": ref.index.max().date(),
            "dentro": float((fuera == 0).mean()), "fuera_max": float(fuera.max()), "malos": malos}


def main() -> None:
    pares = sys.argv[1:] or [p for p in PARES if any((DUKAS / p).glob("*_BID.bi5"))]
    for par in pares:
        try:
            r = contrastar(par)
        except ValueError as exc:
            print(f"{par}: sin contrastar ({exc})")
            continue
        print(f"{par}: {r['dias']} dias ({r['desde']} a {r['hasta']}); el tipo del BCE cae dentro del rango el "
              f"{r['dentro']:.1%} de los dias; lo mas lejos fuera: {r['fuera_max']:.3%}; dias > 0,5 %: {len(r['malos'])}")
        for fecha, v in r["malos"].head(10).items():
            print(f"   {fecha.date()}: {v:.2%} fuera")


if __name__ == "__main__":
    main()
