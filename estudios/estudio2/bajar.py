"""Baja las series del estudio 2 (docs/diseno-estudio-2.md, secciones 1 y 5): los 9 ETF y la referencia.

Solo descarga y describe fechas, huecos y repartos: NO calcula rendimientos (no se mira nada hasta medir la reserva).

Uso: .venv/Scripts/python.exe estudios/estudio2/bajar.py
Salida: var/estudio2/<ticker>.csv (Close, Adj Close, Dividends) y un resumen por pantalla.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
import yfinance as yf

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "var" / "estudio2"

# activo -> serie de Yahoo (seccion 1 del criterio); "referencia" es el indexado mundial (seccion 5)
SERIES = {
    "bolsa_eeuu": "SXR8.DE",
    "bolsa_europa": "EUNK.DE",  # 13/10: era SMEA.MI (huecos de hasta 13 dias en 2013-2014); mismo fondo, linea de Trading 212
    "bolsa_emergente": "EUNM.DE",
    "bonos_euro_estado": "EUNH.DE",
    "bonos_euro_corp": "EUN5.DE",
    "bonos_eeuu_estado": "IUSM.DE",
    "oro": "4GLD.DE",
    "materias_primas": "AIGC.MI",
    "inmobiliario": "IQQ6.DE",
    "referencia": "EUNL.DE",
}


def bajar(ticker: str) -> pd.DataFrame:
    warnings.filterwarnings("ignore")
    df = yf.download(ticker, period="max", interval="1d", auto_adjust=False, actions=True, progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna(subset=["Close"])


def main() -> None:
    DATOS.mkdir(parents=True, exist_ok=True)
    for activo, ticker in SERIES.items():
        df = bajar(ticker)
        cols = [c for c in ("Close", "Adj Close", "Dividends") if c in df]
        df[cols].to_csv(DATOS / f"{activo}.csv")
        f = df.index
        tramo = df.loc["2013-01-01":"2026-09-30"]
        saltos = tramo.index.to_series().diff().dt.days.dropna()
        repartos = int((df.get("Dividends", pd.Series(0, index=f)) > 0).sum())
        print(f"{activo:18} {ticker:8} {f.min().date()} a {f.max().date()} | 2013-2026: {len(tramo)} dias, "
              f"hueco mayor {int(saltos.max())} d | repartos: {repartos}")


if __name__ == "__main__":
    main()
