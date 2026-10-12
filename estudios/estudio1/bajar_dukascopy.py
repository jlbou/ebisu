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
import http.client
import lzma
import random
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "var" / "estudio1" / "dukascopy"
URL = "https://datafeed.dukascopy.com/datafeed/{par}/{anyo}/{mes0:02d}/{lado}_candles_hour_1.bi5"
PARES = ["EURUSD", "USDJPY", "GBPUSD", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
LADOS = ["BID", "ASK"]
DESDE = (2003, 1)
HASTA = (2026, 9)  # ultimo mes cerrado del criterio (reserva hasta el 30/09/2026)
CUENTA = {"ok": 0, "503": 0, "red": 0}


def meses():
    a, m = DESDE
    while (a, m) <= HASTA:
        yield a, m
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def velas(datos: bytes) -> int:
    return len(lzma.decompress(datos)) // 24 if datos else 0


class Conexion:
    """Una sola conexion reutilizada (12/10/2026): abrirla tarda 20-30 s o falla, pero abierta responde al instante.
    El servidor frena a oleadas (503 o corta): entonces se espera cada vez mas (30 s a 5 min) y se reconecta."""

    def __init__(self) -> None:
        self.c: http.client.HTTPSConnection | None = None
        self.espera = 30.0

    def pedir(self, ruta: str) -> bytes | None:
        try:
            if self.c is None:
                self.c = http.client.HTTPSConnection("datafeed.dukascopy.com", timeout=90)
            self.c.request("GET", ruta, headers={"User-Agent": "ebisu-estudio"})
            r = self.c.getresponse()
            datos = r.read()
            if r.will_close:
                self.c.close()
                self.c = None
            if r.status == 200:
                self.espera = 30.0
                CUENTA["ok"] += 1
                return datos
            if r.status == 404:
                CUENTA["ok"] += 1
                return b""
            CUENTA["503" if r.status == 503 else "red"] += 1
        except (OSError, http.client.HTTPException):
            CUENTA["red"] += 1
            if self.c is not None:
                self.c.close()
            self.c = None
        time.sleep(self.espera + random.uniform(0, 5))
        self.espera = min(self.espera * 1.5, 300.0)
        return None


def sano(f: Path) -> bool:
    """Un fichero bajado esta bien si esta vacio (mes sin datos) o se descomprime en registros de 24 bytes."""
    datos = f.read_bytes()
    if not datos:
        return True
    try:
        return len(lzma.decompress(datos)) % 24 == 0
    except lzma.LZMAError:
        return False


def main() -> None:
    # Mientras baja, Windows no se duerme por inactividad (peticion del programa, no cambia ninguna configuracion;
    # se acaba sola al parar el programa). Tapa cerrada o "Suspender" a mano siguen durmiendo el equipo.
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    # Se puede parar en cualquier momento: cada fichero se escribe con un nombre temporal y se renombra al final.
    # Al arrancar se borran los temporales y los ficheros danyados, y se vuelven a pedir.
    for f in DATOS.glob("*/*.tmp"):
        f.unlink()
    malos = [f for f in DATOS.glob("*/*.bi5") if not sano(f)]
    for f in malos:
        f.unlink()
    if malos:
        print(f"{dt.datetime.now():%d/%m %H:%M} ficheros danyados borrados (se vuelven a pedir): {len(malos)}", flush=True)
    pendientes = []
    for par in PARES:
        (DATOS / par).mkdir(parents=True, exist_ok=True)
        for anyo, mes in meses():
            for lado in LADOS:
                destino = DATOS / par / f"{anyo}-{mes:02d}_{lado}.bi5"
                if not destino.exists():
                    ruta = URL.format(par=par, anyo=anyo, mes0=mes - 1, lado=lado).split("dukascopy.com", 1)[1]
                    pendientes.append((destino, ruta))
    print(f"{dt.datetime.now():%d/%m %H:%M} pendientes: {len(pendientes)} (una conexion reutilizada)", flush=True)
    con = Conexion()
    for i, (destino, ruta) in enumerate(pendientes):
        while (datos := con.pedir(ruta)) is None:
            pass  # se reintenta hasta que el servidor responda; la espera crece sola
        tmp = destino.with_suffix(".tmp")
        tmp.write_bytes(datos)
        tmp.replace(destino)
        time.sleep(0.5)
        if (i + 1) % 50 == 0:
            print(f"{dt.datetime.now():%d/%m %H:%M} bajados {i + 1}/{len(pendientes)}, 503: {CUENTA['503']}, "
                  f"red: {CUENTA['red']}", flush=True)
    for par in PARES:
        con_datos = sorted(f.name[:7] for f in (DATOS / par).glob("*_BID.bi5") if velas(f.read_bytes()) > 0)
        print(f"{par}: {len(con_datos)} meses con datos, desde {con_datos[0] if con_datos else '-'}", flush=True)
    print("Terminado", dt.datetime.now().isoformat(timespec="seconds"), flush=True)


if __name__ == "__main__":
    main()
