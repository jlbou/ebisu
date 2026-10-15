"""El juez del papel (decision 11.2; docs/plan-bot-papel.md 3 y 10).

Mira, cada dia, lo que se puede mirar mientras dura el papel; el si final es del propietario:
1. Fidelidad: la estrategia es la misma que el primer dia (huella) y las operaciones cuadran con la estrategia.
2. Sin incidencias: ninguna senyal mensual sin una vuelta del bot ese dia; precios al dia.
3. Caida: no mas que la peor de H1-M en 1971-2026 (14,9 %, estudio 4).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ebisu.papel import Papel

CAIDA_MAX = 0.149


@dataclass(frozen=True)
class Incidencia:
    grave: bool
    tipo: str  # "huella", "coherencia", "caida", "senyal_sin_vuelta", "precios"
    texto: str


def juzgar(papel: Papel, huella_inicio: str, huella_hoy: str, senyales: list[pd.Timestamp],
           dias_con_vuelta: set[pd.Timestamp], avisos_precios: list) -> list[Incidencia]:
    out = []
    if huella_hoy != huella_inicio:
        out.append(Incidencia(True, "huella", "la estrategia ha cambiado desde el primer dia del papel"))
    if len(papel.operaciones) != papel.operaciones_estrategia:
        out.append(Incidencia(True, "coherencia", f"operaciones: {len(papel.operaciones)} contadas, "
                                                  f"{papel.operaciones_estrategia} en la estrategia"))
    if papel.caida > CAIDA_MAX:
        out.append(Incidencia(True, "caida", f"caida del {papel.caida:.1%}, mas que el {CAIDA_MAX:.1%} historico"))
    for s in senyales:
        if s.normalize() not in dias_con_vuelta:
            out.append(Incidencia(True, "senyal_sin_vuelta", f"el {s:%d/%m/%Y} habia senyal y el bot no corrio"))
    for a in avisos_precios:
        out.append(Incidencia(a.tipo in ("salto", "sin_precio"), "precios", f"{a.pieza}: {a.texto}"))
    return out
