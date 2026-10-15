"""Los textos de Telegram (decision 10): cortos, las cifras primero, la IA en una o dos frases. En castellano y siempre
"la IA", nunca el nombre del modelo. Todo texto variable se escapa (HTML de Telegram).
"""

from __future__ import annotations

import html
import re

import pandas as pd

from ebisu.juez import CAIDA_MAX, Incidencia
from ebisu.papel import CAPITAL_EUR, Operacion, Papel

NOMBRES = {"bolsa": "Bolsa (VWCE)", "bonos": "Bonos (CEMF)", "oro": "Oro (SGLD)", "monetario": "Monetario (XEON)"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
CABECERA = "<b>Ebisu · papel</b>"


def e(texto: object) -> str:
    """Escapa para el HTML de Telegram y nunca deja el nombre del modelo."""
    return html.escape(re.sub(r"(?i)claude", "la IA", str(texto)))


def eur(x: float) -> str:
    return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x: float, signo: bool = False) -> str:
    return (f"{x:+.1%}" if signo else f"{x:.1%}").replace(".", ",")


def operaciones(ops: list[Operacion], papel: Papel) -> str:
    lineas = [CABECERA, f"Operaciones del {ops[0].fecha:%d/%m/%Y}:"]
    for o in ops:
        importe = abs(o.despues - o.antes) * papel.valor_eur
        lineas.append(f"• {'Compra' if o.tipo == 'compra' else 'Venta'} {e(NOMBRES[o.pieza])}: "
                      f"{pct(o.antes)} → {pct(o.despues)} (≈ {eur(importe)})")
    lineas.append(f"Valor: {eur(papel.valor_eur)}")
    return "\n".join(lineas)


def resumen_mensual(papel: Papel, ia: str | None, proxima: pd.Timestamp) -> str:
    mes = MESES[papel.ultima_senyal.month - 1]
    lineas = [f"<b>Ebisu · papel · resumen de {mes}</b>",
              f"Valor: {eur(papel.valor_eur)} ({pct(papel.valor_eur / CAPITAL_EUR - 1, True)} desde el inicio)",
              f"VWCE mantenido: {eur(papel.referencia_eur)} ({pct(papel.referencia_eur / CAPITAL_EUR - 1, True)})",
              f"Peor caída: {pct(papel.caida)} (límite {pct(CAIDA_MAX)})",
              "Piezas (medias superadas · peso):"]
    for p, w in papel.pesos.items():
        lineas.append(f"• {e(NOMBRES[p])}: {papel.puntos.get(p, 0)}/4 · {pct(w)}")
    lineas.append(f"La IA: {e(ia)}" if ia else "La IA: sin respuesta este mes")
    lineas.append(f"Próxima revisión: {proxima:%d/%m/%Y}")
    return "\n".join(lineas)


def todo_bien(papel: Papel) -> str:
    return (f"{CABECERA}: todo bien ({papel.hasta:%d/%m}). Valor {eur(papel.valor_eur)}, "
            f"peor caída {pct(papel.caida)}.")


def freno_ia(pieza: str, motivo: str) -> str:
    return (f"{CABECERA}\nLa IA frenaría la compra de {e(NOMBRES.get(pieza, pieza))} "
            f"(en sombra: no se aplica).\nMotivo: {e(motivo)}")


def incidencia(i: Incidencia) -> str:
    return f"{CABECERA}\n{'⚠️ Incidencia grave' if i.grave else 'Aviso'} ({e(i.tipo)}): {e(i.texto)}"
