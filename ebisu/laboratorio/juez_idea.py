"""El juez de la idea 1 (docs/laboratorio/idea-01-rango-del-dia-anterior.md, secciones 4 y 5; criterio APROBADO el 22/10/2026).

Los numeros del criterio estan juntos aqui arriba para que cualquier cambio se vea en git: se fijan ANTES de medir y no se tocan.

Pasa solo si se cumplen las tres:
1. Gana despues de costes: el limite inferior del intervalo de confianza (bootstrap) de la media neta por operacion es > 0,
   con la confianza corregida por el numero de pruebas (Bonferroni: 1 - ALFA / N).
2. Aguanta los costes duros: positiva a 2x los costes base y margen bruto/coste >= MARGEN_MIN a 1x.
3. Caida dentro del limite (CAIDA_MAX del capital asignado, a APALANCAMIENTO).
Parada temprana: a las PARADA_OPS operaciones, si el limite superior del intervalo es negativo, se descarta.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ebisu.laboratorio.regla_rango import Operacion

ALFA = 0.05
MARGEN_MIN = 2.5
CAIDA_MAX = 0.30  # decision 13
MIN_OPERACIONES = 200
MIN_MESES = 3
PARADA_OPERACIONES = 100
CAPITAL_EUR = 250.0
APALANCAMIENTO = 4.0
REMUESTREOS = 10_000
SEMILLA = 7


@dataclass(frozen=True)
class Veredicto:
    estado: str  # "pendiente", "descartada_temprano", "pasa" o "no_pasa"
    razones: tuple[str, ...]
    operaciones: int
    media_neta: float
    limite_inferior: float
    limite_superior: float
    margen: float
    media_neta_2x: float
    caida: float
    dias_sin_compra: int | None


def limites_bootstrap(valores: np.ndarray, confianza: float) -> tuple[float, float]:
    """Limite inferior y superior (a una cola cada uno) de la media, por remuestreo con semilla fija."""
    rng = np.random.default_rng(SEMILLA)
    medias = rng.choice(valores, size=(REMUESTREOS, len(valores)), replace=True).mean(axis=1)
    return float(np.quantile(medias, 1 - confianza)), float(np.quantile(medias, confianza))


def caida_maxima(ops: list[Operacion], capital: float = CAPITAL_EUR, apalancamiento: float = APALANCAMIENTO) -> float:
    """Caida maxima de la curva del capital asignado (ganancias y perdidas sumadas, a `apalancamiento`)."""
    if not ops:
        return 0.0
    ganancias = np.array([op.retorno * apalancamiento * capital for op in ops])
    curva = np.concatenate([[capital], capital + np.cumsum(ganancias)])
    maximos = np.maximum.accumulate(curva)
    return float(np.max((maximos - curva) / maximos))


def juzgar(ops_1x: list[Operacion], ops_2x: list[Operacion], meses: float, n_pruebas: int,
           sesiones: int | None = None) -> Veredicto:
    """`n_pruebas`: las de esta idea MAS las del pasado; se pasa a mano y se publica con el veredicto. `ops_2x`: la
    misma regla simulada con el doble de spread. `sesiones`: las jugadas, solo para contar los dias sin compra."""
    if n_pruebas < 1:
        raise ValueError("n_pruebas tiene que ser >= 1")
    n = len(ops_1x)
    sin_compra = None if sesiones is None else sesiones - n
    if n == 0:
        return Veredicto("pendiente", ("todavia no hay operaciones",), 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, sin_compra)
    confianza = 1 - ALFA / n_pruebas
    netas = np.array([op.neto for op in ops_1x])
    inferior, superior = limites_bootstrap(netas, confianza)
    media = float(netas.mean())
    coste = float(np.mean([op.spread for op in ops_1x]))
    margen = float(np.mean([op.bruto for op in ops_1x]) / coste) if coste > 0 else float("inf")
    media_2x = float(np.mean([op.neto for op in ops_2x])) if ops_2x else 0.0
    caida = caida_maxima(ops_1x)

    def veredicto(estado: str, razones: list[str]) -> Veredicto:
        return Veredicto(estado, tuple(razones), n, media, inferior, superior, margen, media_2x, caida, sin_compra)

    if n >= PARADA_OPERACIONES and superior < 0:
        return veredicto("descartada_temprano", [f"a las {n} operaciones el limite superior de la media es negativo"])
    if n < MIN_OPERACIONES or meses < MIN_MESES:
        return veredicto("pendiente", [f"{n} de {MIN_OPERACIONES} operaciones y {meses:.1f} de {MIN_MESES} meses"])
    fallos = []
    if inferior <= 0:
        fallos.append("el limite inferior de la media neta no es positivo")
    if media_2x <= 0:
        fallos.append("a 2x los costes la media neta no es positiva")
    if margen < MARGEN_MIN:
        fallos.append(f"el margen bruto/coste es {margen:.2f}, menos de {MARGEN_MIN}")
    if caida >= CAIDA_MAX:
        fallos.append(f"la caida es del {caida:.1%}, no menos del {CAIDA_MAX:.0%}")
    return veredicto("no_pasa" if fallos else "pasa", fallos)
