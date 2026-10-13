"""Baja los datos auxiliares del estudio 3 (docs/plan-estudio-3.md 3 y 13.3): el VIX y los tipos oficiales.

- VIX (escenario 4, huida del riesgo): cierre diario de FRED (VIXCLS), desde 1990.
- Tipos oficiales de los bancos centrales, diarios (BIS, WS_CBPOL): para los intereses de cada noche.

Solo descarga y describe fechas y huecos; no calcula nada de la estrategia.

Uso: .venv/Scripts/python.exe estudios/estudio3/bajar.py
Salida: var/estudio3/vix.csv y var/estudio3/tipos.csv (una columna por divisa, en %).
"""

from __future__ import annotations

import io
import time
import urllib.request
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "var" / "estudio3"
# divisa -> zona del BIS (XM = zona euro). SGD no tiene tipo oficial (la MAS no lo fija): se resuelve con los pares nuevos.
ZONAS = {"USD": "US", "EUR": "XM", "GBP": "GB", "JPY": "JP", "CHF": "CH", "AUD": "AU", "CAD": "CA", "NZD": "NZ",
         "NOK": "NO", "SEK": "SE", "MXN": "MX", "ZAR": "ZA"}


def leer(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ebisu-estudio)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def vix() -> pd.Series:
    df = pd.read_csv(io.BytesIO(leer("https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS")), na_values=".")
    df.columns = ["fecha", "vix"]
    return df.set_index(pd.to_datetime(df["fecha"]))["vix"].dropna()


def tipo(zona: str) -> pd.Series:
    """API oficial del BIS (la copia de DBnomics llegaba solo a 07/2025)."""
    url = f"https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBPOL/1.0/D.{zona}?format=csv&startPeriod=2000-01-01"
    for intento in range(5):  # a veces devuelve vacio (limite de peticiones): se espera y se repite
        datos = leer(url)
        if datos.strip():
            break
        time.sleep(20 * (intento + 1))
    df = pd.read_csv(io.BytesIO(datos), usecols=["TIME_PERIOD", "OBS_VALUE"])
    return pd.Series(pd.to_numeric(df["OBS_VALUE"], errors="coerce").to_numpy(),
                     index=pd.to_datetime(df["TIME_PERIOD"])).dropna()


def main() -> None:
    DATOS.mkdir(parents=True, exist_ok=True)
    v = vix()
    v.to_csv(DATOS / "vix.csv", header=True)
    print(f"VIX: {v.index.min().date()} a {v.index.max().date()}, {len(v)} dias")
    tipos = {}
    for divisa, zona in ZONAS.items():
        s = tipo(zona)
        tipos[divisa] = s
        hueco = s.loc["2002":].index.to_series().diff().dt.days.max()
        print(f"{divisa} ({zona}): {s.index.min().date()} a {s.index.max().date()}, {len(s)} dias, hueco max. desde 2002 {hueco} dias")
    pd.DataFrame(tipos).sort_index().to_csv(DATOS / "tipos.csv")


if __name__ == "__main__":
    main()
