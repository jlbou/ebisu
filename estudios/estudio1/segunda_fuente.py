"""Contraste de las series de Yahoo con una segunda fuente independiente (docs/diseno-estudio-1.md, seccion 2).

- Fondos y ETF de EE. UU.: Nasdaq (api.nasdaq.com, la misma que usa su web), cierre SIN ajustar contra el cierre sin
  ajustar de Yahoo, dia a dia, en las fechas comunes. Regla fijada: diferencia > 0,5 % en algun dia sin explicacion
  -> se para y se decide.
- Letra del Tesoro a 13 semanas: Yahoo (^IRX) contra la Reserva Federal (FRED, DTB3), oficial. Es un tipo en %, asi
  que se compara la diferencia en puntos.

NO calcula rendimientos. Uso: .venv/Scripts/python.exe estudios/estudio1/segunda_fuente.py
"""

from __future__ import annotations

import io
import json
import urllib.request
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
YAHOO = RAIZ / "var" / "inventario"
SALIDA = RAIZ / "var" / "estudio1" / "segunda_fuente"
UA = {"User-Agent": "ebisu-estudio", "Accept": "application/json"}
NASDAQ = ("https://api.nasdaq.com/api/quote/{t}/historical?assetclass={c}"
          "&fromdate=1990-01-01&todate=2026-10-10&limit=20000")
SERIES = [("VTSMX", "mutualfunds"), ("VGTSX", "mutualfunds"), ("VBMFX", "mutualfunds"), ("GLD", "etf")]


def leer(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def nasdaq(ticker: str, clase: str) -> pd.Series:
    filas = json.loads(leer(NASDAQ.format(t=ticker, c=clase)))["data"]["tradesTable"]["rows"]
    s = pd.Series({pd.Timestamp(f["date"]): float(f["close"].replace("$", "").replace(",", "")) for f in filas})
    return s.sort_index()


def yahoo(nombre: str) -> pd.Series:
    df = pd.read_csv(YAHOO / f"{nombre}.csv", index_col=0, parse_dates=True)
    return df["Close"].astype(float)


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    for ticker, clase in SERIES:
        n = nasdaq(ticker, clase)
        n.to_csv(SALIDA / f"nasdaq_{ticker}.csv", header=["close"])
        y = yahoo(ticker)
        comun = y.index.intersection(n.index)
        dif = (y[comun] / n[comun] - 1).abs()
        malos = dif[dif > 0.005]
        print(f"{ticker}: {len(comun)} dias comunes ({comun.min().date()} a {comun.max().date()}); "
              f"diferencia mediana {dif.median():.5%}, maxima {dif.max():.3%}; dias > 0,5 %: {len(malos)}")
        if len(malos):
            print("   primeros:", ", ".join(f"{d.date()} ({v:.2%})" for d, v in malos.head(8).items()))

    fred = pd.read_csv(io.BytesIO(leer("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3")),
                       index_col=0, parse_dates=True, na_values=".")["DTB3"].dropna()
    fred.to_csv(SALIDA / "fred_DTB3.csv")
    y = yahoo("_IRX")
    comun = y.index.intersection(fred.index)
    dif = (y[comun] - fred[comun]).abs()
    print(f"^IRX frente a DTB3: {len(comun)} dias comunes; diferencia mediana {dif.median():.3f} puntos, "
          f"maxima {dif.max():.3f}; dias > 0,05 puntos: {(dif > 0.05).sum()}")


if __name__ == "__main__":
    main()
