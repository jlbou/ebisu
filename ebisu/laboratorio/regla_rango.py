"""Idea 1 del laboratorio: el rango del dia anterior (docs/laboratorio/idea-01-rango-del-dia-anterior.md).

Cada sesion, con el rango (maximo y minimo) de la sesion anterior, se fijan dos niveles:
    compra   = minimo + x * rango      objetivo = maximo - x * rango
Una orden de compra espera en `compra`; con compra hecha, se vende en `objetivo` o, si no llega, al final de la sesion.

Reglas de simulacion (todas del lado prudente):
- La sesion termina a las 17:00 de Nueva York (22:00 UTC en invierno, 21:00 UTC en verano).
- Con precios medios y un spread `s`: la compra entra solo si el precio medio baja a `compra - s/2` (el precio de venta
  del broker llega al nivel) y la venta solo si sube a `objetivo + s/2`. Tocar el nivel no basta.
- Una operacion como mucho por sesion y par. La salida se mira desde la barra SIGUIENTE a la de la entrada (dentro de
  una barra no se sabe el orden de los precios). Si la entrada es en la ultima barra, se cierra en ella.
- Una sola posicion abierta en total (`una_posicion`): una orden que llega con otra abierta no se ejecuta.
Las barras deben ser de la sesion completa: una sesion a medias daria un rango incorrecto.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

NY = "America/New_York"
HORA_CORTE_NY = 17


@dataclass(frozen=True)
class Operacion:
    par: str
    sesion: pd.Timestamp
    entrada: pd.Timestamp
    salida: pd.Timestamp
    precio_entrada: float
    precio_salida: float
    spread: float  # coste de un viaje en precio
    motivo: str  # "objetivo" o "cierre"

    @property
    def neto(self) -> float:
        """Ganancia en precio, ya despues del spread (la entrada paga el precio de compra y la salida cobra el de venta)."""
        return self.precio_salida - self.precio_entrada

    @property
    def bruto(self) -> float:
        """Lo que habria ganado sin spread."""
        return self.neto + self.spread

    @property
    def retorno(self) -> float:
        return self.neto / self.precio_entrada


def etiquetar_sesiones(indice: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """A que sesion (con el nombre del dia en que termina) pertenece cada barra. Hora local de Nueva York, sin
    depender de si es horario de verano."""
    if indice.tz is None:
        raise ValueError("el indice tiene que llevar zona horaria (UTC)")
    local = indice.tz_convert(NY).tz_localize(None)
    return (local + pd.Timedelta(hours=24 - HORA_CORTE_NY)).normalize()


def rangos_por_sesion(barras: pd.DataFrame) -> pd.DataFrame:
    g = barras.groupby(etiquetar_sesiones(barras.index))
    return pd.DataFrame({"high": g["high"].max(), "low": g["low"].min()})


def niveles(maximo: float, minimo: float, x: float) -> tuple[float, float]:
    """(compra, objetivo) para una sesion, a partir del maximo y el minimo de la anterior."""
    if not 0 <= x < 0.5:
        raise ValueError("x tiene que estar en [0, 0,5)")
    rango = maximo - minimo
    if rango <= 0:
        raise ValueError("el rango de ayer tiene que ser positivo")
    return minimo + x * rango, maximo - x * rango


def simular_sesion(par: str, sesion: pd.Timestamp, barras: pd.DataFrame, compra: float, objetivo: float,
                   spread: float) -> Operacion | None:
    """Una sesion: `barras` con high, low y close (precios medios), en orden. None si no hay compra."""
    mitad = spread / 2
    bajos = barras["low"].to_numpy()
    entradas = np.flatnonzero(bajos <= compra - mitad)
    if len(entradas) == 0:
        return None
    i = int(entradas[0])
    siguientes = barras["high"].to_numpy()[i + 1:]
    llegadas = np.flatnonzero(siguientes >= objetivo + mitad)
    if len(llegadas):
        j = i + 1 + int(llegadas[0])
        precio_salida, motivo = objetivo, "objetivo"
    else:
        j = len(barras) - 1
        precio_salida, motivo = float(barras["close"].iloc[j]) - mitad, "cierre"
    return Operacion(par, sesion, barras.index[i], barras.index[j], compra, precio_salida, spread, motivo)


def simular(par: str, barras: pd.DataFrame, x: float, spread: float) -> list[Operacion]:
    """Todas las sesiones de `barras` (menos la primera, que solo da el rango). Los dias sin compra no dan operacion."""
    etiquetas = etiquetar_sesiones(barras.index)
    rangos = rangos_por_sesion(barras)
    ops = []
    for k in range(1, len(rangos)):
        ayer = rangos.iloc[k - 1]
        if ayer["high"] - ayer["low"] <= 0:
            continue
        compra, objetivo = niveles(float(ayer["high"]), float(ayer["low"]), x)
        sesion = rangos.index[k]
        op = simular_sesion(par, sesion, barras[etiquetas == sesion], compra, objetivo, spread)
        if op is not None:
            ops.append(op)
    return ops


def una_posicion(*listas: list[Operacion]) -> list[Operacion]:
    """Junta las operaciones de varios pares con una sola posicion abierta en total: una operacion cuya entrada cae
    antes de la salida de la anterior aceptada no se ejecuta."""
    todas = sorted((op for lista in listas for op in lista), key=lambda op: op.entrada)
    out: list[Operacion] = []
    for op in todas:
        if not out or op.entrada >= out[-1].salida:
            out.append(op)
    return out
