"""Baja del Banco Central Europeu (fuente oficial) el cambio euro/dolar, el EONIA y el STR.

Solo descarga y describe fechas y huecos: NO calcula rendimientos (criterio: docs/diseno-estudio-1.md, seccion 2).

Uso: .venv/Scripts/python.exe estudios/estudio1/bajar_bce.py
Salida: var/estudio1/bce_<serie>.csv (fecha, valor) y un resumen por pantalla.
"""

from __future__ import annotations

import csv
import io
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "var" / "estudio1"
API = "https://data-api.ecb.europa.eu/service/data/{clave}?format=csvdata&startPeriod=1999-01-01"

SERIES = {
    "eurusd": "EXR/D.USD.EUR.SP00.A",  # dolares por euro, referencia del BCE a las 14:15 CET
    "eonia": "EON/D.EONIA_TO.RATE",  # tipo a un dia del euro, % anual (1999-2021)
    "estr": "EST/B.EU000A2X2A25.WT",  # STR, % anual (desde 10/2019)
}


def bajar(clave: str) -> list[tuple[str, float]]:
    pet = urllib.request.Request(API.format(clave=clave), headers={"User-Agent": "ebisu-estudio"})
    with urllib.request.urlopen(pet, timeout=120) as resp:
        texto = resp.read().decode("utf-8")
    filas = []
    for fila in csv.DictReader(io.StringIO(texto)):
        if fila.get("OBS_VALUE"):
            filas.append((fila["TIME_PERIOD"], float(fila["OBS_VALUE"])))
    return sorted(filas)


def main() -> None:
    DATOS.mkdir(parents=True, exist_ok=True)
    import pandas as pd

    for nombre, clave in SERIES.items():
        filas = bajar(clave)
        destino = DATOS / f"bce_{nombre}.csv"
        with destino.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["fecha", "valor"])
            w.writerows(filas)
        fechas = pd.to_datetime([f for f, _ in filas])
        saltos = pd.Series(fechas).diff().dt.days.dropna()
        print(f"{nombre}: {len(filas)} filas, {fechas.min().date()} a {fechas.max().date()}, "
              f"hueco mayor {int(saltos.max())} dias")


if __name__ == "__main__":
    main()
