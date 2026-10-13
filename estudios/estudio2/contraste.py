"""Contraste diario de las series del estudio 2 con la misma cartera en otra bolsa (docs/diseno-estudio-2.md, 6.2 y 7).

Para cada activo: la serie del estudio (var/estudio2/) frente a otra cotizacion en euros del mismo fondo (o, en el oro,
otro ETC de oro fisico). Se mira el cociente de los dos cierres frente a su mediana de 21 dias habiles: si se aparta
mas de un 0,5 % algun dia, se avisa (un error de datos de un dia salta asi; las diferencias lentas de comisiones, no).

NO calcula rendimientos. Uso: .venv/Scripts/python.exe estudios/estudio2/contraste.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
import yfinance as yf

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "var" / "estudio2"
UMBRAL = 0.005
TRAMO = ("2013-01-01", "2026-09-30")

SEGUNDA = {
    "bolsa_eeuu": "CSSPX.MI",
    "bolsa_europa": "IMAE.AS",
    "bolsa_emergente": "IEMA.AS",
    "bonos_euro_estado": "IEGA.AS",
    "bonos_euro_corp": "IEAC.AS",
    "bonos_eeuu_estado": "BTMA.AS",
    "oro": "SGLD.MI",
    "materias_primas": "AIGCP.PA",
    "inmobiliario": "IWDP.AS",
    "referencia": "IWDA.AS",
}


def cierre(ticker: str) -> pd.Series:
    warnings.filterwarnings("ignore")
    df = yf.download(ticker, period="max", interval="1d", auto_adjust=False, progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df["Close"].dropna()


def main() -> None:
    DATOS.mkdir(parents=True, exist_ok=True)
    for activo, otro in SEGUNDA.items():
        a = pd.read_csv(DATOS / f"{activo}.csv", index_col=0, parse_dates=True)["Close"]
        b = cierre(otro)
        b.to_csv(DATOS / f"segunda_{activo}.csv", header=["Close"])
        comun = a.index.intersection(b.index)
        comun = comun[(comun >= TRAMO[0]) & (comun <= TRAMO[1])]
        r = a[comun] / b[comun]
        desvio = (r / r.rolling(21, center=True, min_periods=5).median() - 1).abs()
        malos = desvio[desvio > UMBRAL]
        print(f"{activo:18} frente a {otro:9} {len(comun)} dias comunes ({comun.min().date()} a {comun.max().date()}); "
              f"desvio mediano {desvio.median():.3%}, maximo {desvio.max():.2%}; dias > 0,5 %: {len(malos)}")
        for f, v in malos.head(6).items():
            print(f"    {f.date()}: {v:.2%}")


if __name__ == "__main__":
    main()
