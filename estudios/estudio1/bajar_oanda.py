"""Baja de OANDA (cuenta de PRACTICA, sin dinero) las velas diarias de compra y de venta de los 7 pares de H2.

Las velas vienen cortadas a las 17:00 de Nueva York (dailyAlignment=17, alignmentTimezone=America/New_York), la
definicion de dia del criterio (docs/diseno-estudio-1.md, H2 y seccion 9). Solo velas completas.

El token se lee del .env (OANDA_TOKEN) y no se escribe nunca en pantalla ni en ficheros. Si falta, el script para.
Solo descarga y describe fechas: NO calcula rendimientos.

Uso: .venv/Scripts/python.exe estudios/estudio1/bajar_oanda.py
Salida: var/estudio1/oanda/<PAR>.csv (fecha de cierre de la vela, apertura/maximo/minimo/cierre de compra y de venta) y un resumen.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "var" / "estudio1" / "oanda"
HOSTS = {"practice": "https://api-fxpractice.oanda.com"}
PARES = ["EUR_USD", "USD_JPY", "GBP_USD", "USD_CHF", "AUD_USD", "USD_CAD", "NZD_USD"]
DESDE = "2000-01-01T00:00:00Z"
HASTA = "2026-10-01T00:00:00Z"
POR_PETICION = 4000  # el maximo de OANDA es 5000


def leer_env() -> dict[str, str]:
    valores = {}
    for linea in (RAIZ / ".env").read_text(encoding="utf-8-sig").splitlines():
        if "=" in linea and not linea.lstrip().startswith("#"):
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip()
    return valores


def pedir(url: str, token: str) -> dict:
    pet = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept-Datetime-Format": "RFC3339"})
    for intento in range(5):
        try:
            with urllib.request.urlopen(pet, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise SystemExit(f"OANDA rechaza el token (HTTP {exc.code}): revisa OANDA_TOKEN en el .env") from None
            if exc.code != 429 and exc.code < 500:
                raise SystemExit(f"OANDA respondio HTTP {exc.code} para {url.split('?')[0]}") from None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            pass
        time.sleep(2 * (intento + 1))
    raise SystemExit("OANDA no responde tras varios intentos")


def bajar_par(par: str, host: str, token: str) -> list[list]:
    filas, desde = [], DESDE
    while True:
        q = urllib.parse.urlencode({
            "granularity": "D", "price": "BA", "dailyAlignment": 17, "alignmentTimezone": "America/New_York",
            "from": desde, "count": POR_PETICION, "includeFirst": "false" if filas else "true",
        })
        velas = pedir(f"{host}/v3/instruments/{par}/candles?{q}", token).get("candles", [])
        nuevas = [v for v in velas if v.get("complete") and v["time"] < HASTA]
        for v in nuevas:
            b, a = v["bid"], v["ask"]
            # OANDA fecha la vela por su inicio (17:00 de Nueva York del dia anterior): se etiqueta con el dia
            # en que se cierra.
            inicio = dt.datetime.fromisoformat(v["time"][:19])
            filas.append([(inicio + dt.timedelta(days=1)).date().isoformat(), b["o"], b["h"], b["l"], b["c"], a["o"], a["h"], a["l"], a["c"]])
        if len(velas) < POR_PETICION or not nuevas or velas[-1]["time"] >= HASTA:
            return filas
        desde = velas[-1]["time"]
        time.sleep(0.5)


def main() -> None:
    env = leer_env()
    token, entorno = env.get("OANDA_TOKEN", ""), env.get("OANDA_ENTORNO", "practice")
    if not token:
        raise SystemExit("Falta OANDA_TOKEN en el .env (lo pone el propietario; no se pega en el chat)")
    if entorno not in HOSTS:
        raise SystemExit("OANDA_ENTORNO tiene que ser 'practice': este estudio no usa la cuenta real")
    DATOS.mkdir(parents=True, exist_ok=True)
    for par in PARES:
        filas = bajar_par(par, HOSTS[entorno], token)
        with (DATOS / f"{par}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["fecha", "bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"])
            w.writerows(filas)
        print(f"{par}: {len(filas)} dias, {filas[0][0] if filas else '-'} a {filas[-1][0] if filas else '-'}", flush=True)


if __name__ == "__main__":
    main()
