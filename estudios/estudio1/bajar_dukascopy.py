"""Baja de Dukascopy (banco suizo) las velas de 1 hora, de compra y de venta, de los 7 pares principales.

Sin dependencias nuevas: los ficheros .bi5 son LZMA con registros de 24 bytes (segundos desde el inicio del mes,
apertura, cierre, minimo, maximo en enteros, volumen). Se baja por meses, despacio y con reintentos (el servidor
corta conexiones y da 503 si se le pide deprisa); lo ya bajado no se vuelve a pedir.

Solo descarga y describe fechas: NO calcula rendimientos (docs/diseno-estudio-1.md, seccion 3, H2).
Las velas de 1 hora se agrupan despues en dias de 17:00 a 17:00 de Nueva York (otro script).

Uso: .venv/Scripts/python.exe estudios/estudio1/bajar_dukascopy.py
Salida: var/estudio1/dukascopy/<PAR>/<anyo>-<mes>_<LADO>.bi5 y un resumen por par.
"""

from __future__ import annotations

import datetime as dt
import lzma
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import random
import struct
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "var" / "estudio1" / "dukascopy"
URL = "https://datafeed.dukascopy.com/datafeed/{par}/{anyo}/{mes0:02d}/{lado}_candles_hour_1.bi5"
PARES = ["EURUSD", "USDJPY", "GBPUSD", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
LADOS = ["BID", "ASK"]
DESDE = (2003, 1)
HASTA = (2026, 9)  # ultimo mes cerrado del criterio (reserva hasta el 30/09/2026)
PAUSA = 3.0  # segundos entre peticiones (con menos, el servidor responde 503)
REINTENTOS = 8
HILOS = int(os.environ.get("EBISU_HILOS", "1"))  # peticiones a la vez (prueba con 2, 12/10/2026)
CUENTA = {"ok": 0, "503": 0, "red": 0}
_CERROJO = threading.Lock()


def meses():
    a, m = DESDE
    while (a, m) <= HASTA:
        yield a, m
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def pedir(url: str) -> bytes | None:
    """Devuelve el fichero (b'' si el mes no tiene datos) o None si no se pudo tras los reintentos."""
    espera = 5.0
    for _ in range(REINTENTOS):
        try:
            pet = urllib.request.Request(url, headers={"User-Agent": "ebisu-estudio"})
            with urllib.request.urlopen(pet, timeout=90) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return b""
            with _CERROJO:
                CUENTA["503" if exc.code == 503 else "red"] += 1
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            with _CERROJO:
                CUENTA["red"] += 1
        time.sleep(espera + random.uniform(0, 2))
        espera = min(espera * 2, 120)
    return None


def velas(datos: bytes) -> int:
    return len(lzma.decompress(datos)) // 24 if datos else 0


def tarea(destino: Path, url: str, fallos: list) -> None:
    datos = pedir(url)
    time.sleep(PAUSA)
    if datos is None:
        fallos.append(destino.name)
        print("FALLO", destino.parent.name, destino.name, flush=True)
        return
    destino.write_bytes(datos)
    with _CERROJO:
        CUENTA["ok"] += 1
        if CUENTA["ok"] % 5 == 0:
            print(f"{dt.datetime.now():%H:%M} bajados {CUENTA['ok']}, 503: {CUENTA['503']}, red: {CUENTA['red']}",
                  flush=True)


def main() -> None:
    fallos: list = []
    pendientes = []
    for par in PARES:
        (DATOS / par).mkdir(parents=True, exist_ok=True)
        for anyo, mes in meses():
            for lado in LADOS:
                destino = DATOS / par / f"{anyo}-{mes:02d}_{lado}.bi5"
                if not destino.exists():
                    pendientes.append((destino, URL.format(par=par, anyo=anyo, mes0=mes - 1, lado=lado)))
    print(f"{dt.datetime.now():%H:%M} pendientes: {len(pendientes)}, hilos: {HILOS}", flush=True)
    with ThreadPoolExecutor(max_workers=HILOS) as ex:
        for destino, url in pendientes:
            ex.submit(tarea, destino, url, fallos)
    for par in PARES:
        con_datos = sorted(f.name[:7] for f in (DATOS / par).glob("*_BID.bi5") if velas(f.read_bytes()) > 0)
        print(f"{par}: {len(con_datos)} meses con datos, desde {con_datos[0] if con_datos else '-'}", flush=True)
    print(f"Fallos (se reintentan al volver a lanzar): {len(fallos)}; 503: {CUENTA['503']}, red: {CUENTA['red']}",
          flush=True)
    print("Terminado", dt.datetime.now().isoformat(timespec="seconds"), flush=True)


if __name__ == "__main__":
    main()
