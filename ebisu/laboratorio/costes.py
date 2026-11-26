"""Costes de las divisas en papel. El spread es un PARAMETRO: ningun valor esta verificado con cuenta de FOREX.com."""

from __future__ import annotations

PIP = {"EURUSD": 0.0001, "USDJPY": 0.01}  # tamanyo de un pip en precio (con el ien, la segunda cifra decimal)

# [Sin verificar] Pesimista por defecto: el de Trading 212 (~1,2 pips en EUR/USD), para los dos pares.
SPREAD_PIPS_PESIMISTA = 1.2
# [Sin verificar] El publicado por FOREX.com para EUR/USD en una pagina antigua; falta confirmarlo en su plataforma.
SPREAD_PIPS_FOREXCOM_EURUSD = 0.7


def spread_en_precio(par: str, pips: float = SPREAD_PIPS_PESIMISTA, multiplo: float = 1.0) -> float:
    """El spread de un viaje (compra y venta) en unidades de precio; `multiplo` es el 1x, 2x o 3x de los costes base."""
    if par not in PIP:
        raise ValueError(f"par desconocido: {par}")
    if pips < 0 or multiplo < 0:
        raise ValueError("el spread y su multiplo no pueden ser negativos")
    return PIP[par] * pips * multiplo
