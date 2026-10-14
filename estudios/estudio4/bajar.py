"""Baja las fuentes del estudio 4 (docs/plan-estudio-4.md 3 y 13) a var/estudio4/fuentes/.

Solo descarga y describe fechas; no calcula nada de ninguna estrategia. Lo que ya bajo el estudio 1 (BCE, DTB3, ETF
reales, GC=F) se lee de var/estudio1 y var/inventario, no se repite.

Uso: .venv/Scripts/python.exe estudios/estudio4/bajar.py
"""

from __future__ import annotations

import io
import json
import time
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FUENTES = RAIZ / "var" / "estudio4" / "fuentes"
FRENCH = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
BBK = "https://api.statistiken.bundesbank.de/rest/download/BBEX3/"
MSCI = ("https://app2.msci.com/products/service/index/indexmaster/getLevelDataForGraph?currency_symbol=USD"
        "&index_variant={v}&start_date=19970101&end_date=20261001&data_frequency=DAILY&index_codes=990300")

ZIPS = {  # nombre local -> fichero de Kenneth French
    "french_diario": "F-F_Research_Data_Factors_daily_CSV.zip",
    "french_mensual": "F-F_Research_Data_Factors_CSV.zip",
    "french_49_sectores": "49_Industry_Portfolios_CSV.zip",
    "french_internacional": "F-F_International_Indices.zip",
}
SERIES_FRED = ["DGS7", "DTB3", "IRSTCI01DEM156N", "CPIAUCNS", "CPIAUCSL"]
SERIES_BBK = {"bbk_dem_usd": "D.USD.DEM.AA.AC.000", "bbk_oro_frankfurt": "D.XAU.DEM.EA.AC.C01"}


def leer(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ebisu-estudio)"})
    for intento in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except OSError:
            if intento == 3:
                raise
            time.sleep(15 * (intento + 1))
    raise RuntimeError(url)


def guardar(nombre: str, datos: bytes) -> None:
    (FUENTES / nombre).write_bytes(datos)
    print(f"{nombre}: {len(datos):,} bytes")


def main() -> None:
    FUENTES.mkdir(parents=True, exist_ok=True)
    for nombre, fichero in ZIPS.items():
        z = zipfile.ZipFile(io.BytesIO(leer(FRENCH + fichero)))
        destino = FUENTES / nombre
        destino.mkdir(exist_ok=True)
        z.extractall(destino)
        print(f"{nombre}: {', '.join(z.namelist())}")
    for s in SERIES_FRED:
        guardar(f"fred_{s}.csv", leer(FRED + s))
    for nombre, clave in SERIES_BBK.items():
        guardar(f"{nombre}.csv", leer(f"{BBK}{clave}?format=csv&lang=en"))
    for v, nombre in (("GRTR", "msci_eafe_con_div"), ("STRD", "msci_eafe_precio")):
        niveles = json.loads(leer(MSCI.format(v=v)))["indexes"]["INDEX_LEVELS"]
        filas = "fecha,nivel\n" + "".join(f"{n['calc_date']},{n['level_eod']}\n" for n in niveles)
        guardar(f"{nombre}.csv", filas.encode())
    guardar("datahub_oro_mensual.csv", leer("https://datahub.io/core/gold-prices/r/monthly.csv"))


if __name__ == "__main__":
    main()
