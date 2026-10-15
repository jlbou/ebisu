"""El papel de H1-M (docs/plan-bot-papel.md 3): se rehace entero cada dia con la estrategia del estudio.

- Las piezas salen de los cierres guardados (ebisu/precios.py): calendario de la union de dias de las 4 bolsas, con el
  ultimo cierre conocido en los festivos de cada una (como en el estudio).
- El papel empieza el dia de EJECUCION de la primera senyal (el dia habil siguiente), en el monetario.
- H1-M del bot: la del estudio sin gasto extra (los precios de los ETF ya lo llevan); 0,10 % por lado.
- Las operaciones se sacan de los pesos objetivo y de su dia de ejecucion (la misma regla que la estrategia); una
  prueba comprueba que su numero coincide con el que cuenta la estrategia.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from ebisu import estrategia as E

CAPITAL_EUR = 250.0
PIEZAS = ("bolsa", "bonos", "oro")
H1M = E.Variante("H1-M")  # sin gasto extra: el ETF ya lo lleva en el precio


@dataclass(frozen=True)
class Operacion:
    fecha: pd.Timestamp  # dia de ejecucion (cierre)
    pieza: str
    antes: float  # peso objetivo anterior
    despues: float

    @property
    def tipo(self) -> str:
        return "compra" if self.despues > self.antes else "venta"


@dataclass
class Papel:
    hasta: pd.Timestamp
    valor_eur: float  # valor del dia (impuestos ya pagados restados)
    si_vende_hoy_eur: float  # lo que quedaria tras venderlo todo y pagar lo pendiente
    caida: float  # peor caida desde un maximo, desde el inicio
    referencia_eur: float  # VWCE mantenido desde el inicio (sin vender)
    pesos: dict[str, float]  # pesos objetivo vigentes
    operaciones: list[Operacion] = field(default_factory=list)
    operaciones_estrategia: int = 0  # las que cuenta la estrategia (para la prueba de coherencia)
    puntos: dict[str, int] = field(default_factory=dict)  # medias superadas (0-4) en la ultima senyal
    ultima_senyal: pd.Timestamp | None = None
    valor: pd.Series | None = None
    referencia: pd.Series | None = None  # VWCE mantenido, por euro inicial
    impuestos_eur: float = 0.0  # impuestos simulados pagados hasta hoy


def piezas_de(cierres: pd.DataFrame) -> pd.DataFrame:
    """Cierres en euros -> piezas: union de dias, ultimo cierre conocido en festivos, solo dias laborables."""
    p = cierres.sort_index().ffill()
    return p[p.index.dayofweek < 5]


def ultimo_dia_completo(cierres: pd.DataFrame) -> pd.Timestamp:
    """El ultimo dia hasta el que hay cierre de las 4 piezas (cada una, su ultimo cierre guardado)."""
    return min(cierres[c].last_valid_index() for c in cierres.columns)


def senyales_reales(piezas: pd.DataFrame, hasta: pd.Timestamp) -> pd.DatetimeIndex:
    """Los dias de senyal ya seguros: el ultimo dia con precios de cada mes terminado, y el de hoy si hoy es el ultimo
    dia habil del mes. (Para la estrategia, el ultimo dia con datos de un mes a medias tambien es "senyal", pero su
    ejecucion seria manyana y manyana deja de serlo: nunca se ejecuta.)"""
    s = E.dias_de_senyal(piezas.loc[:hasta].index)
    fin_de_mes = hasta == (hasta + pd.offsets.BMonthEnd(0))
    return s if fin_de_mes else s[s.to_period("M") < hasta.to_period("M")]


def dia_de_ejecucion(piezas: pd.DataFrame, senyal: pd.Timestamp) -> pd.Timestamp | None:
    i = piezas.index.get_loc(senyal) + H1M.retraso
    return piezas.index[i] if i < len(piezas.index) else None


def operaciones(piezas: pd.DataFrame, inicio: pd.Timestamp, hasta: pd.Timestamp) -> tuple[list[Operacion], dict]:
    """Cambios de peso objetivo ejecutados entre inicio y hasta (misma regla que la estrategia)."""
    objetivo = E.pesos_objetivo(piezas.loc[:hasta], H1M)
    actual: dict[str, float] = {}
    ops = []
    for senyal, fila in objetivo.iterrows():
        dia = dia_de_ejecucion(piezas, senyal)
        if dia is None or not (inicio <= dia <= hasta):
            continue
        for p in PIEZAS:
            w = float(fila[p])
            if p not in actual or abs(actual[p] - w) >= 1e-12:
                if not (p not in actual and w == 0.0):  # estar a 0 desde el principio no es una operacion
                    ops.append(Operacion(dia, p, actual.get(p, 0.0), w))
                actual[p] = w
    return ops, actual


def calcular(cierres: pd.DataFrame, primera_senyal: pd.Timestamp, hasta: pd.Timestamp) -> Papel:
    """El papel desde el dia de ejecucion de la primera senyal hasta `hasta` (incluido), pero nunca mas alla del ultimo
    dia en que las 4 piezas tienen cierre guardado: si una se retrasa, no se rellena con un precio viejo (la senyal del
    mes podria salir con un cierre de ayer)."""
    hasta = min(hasta, ultimo_dia_completo(cierres))
    piezas = piezas_de(cierres).loc[:hasta]
    inicio = dia_de_ejecucion(piezas, primera_senyal)
    if inicio is None:
        raise ValueError("todavia no hay dia de ejecucion para la primera senyal")
    r = E.simular(piezas, H1M, str(inicio.date()), str(hasta.date()))
    ref = E.referencia(piezas, str(inicio.date()), str(hasta.date()), gasto=0.0, impuestos=False)
    ops, pesos = operaciones(piezas, inicio, hasta)
    v = r.valor
    ultima = senyales_reales(piezas, hasta)[-1]
    puntos = {pz: int(E.medias_superadas(piezas[pz]).loc[ultima]) for pz in PIEZAS}
    return Papel(hasta=v.index[-1], valor_eur=CAPITAL_EUR * float(v.iloc[-1]),
                 si_vende_hoy_eur=CAPITAL_EUR * r.bolsillo, caida=float((1 - v / v.cummax()).max()),
                 referencia_eur=CAPITAL_EUR * float(ref.valor.iloc[-1]), pesos=pesos, operaciones=ops,
                 operaciones_estrategia=r.operaciones, puntos=puntos, ultima_senyal=ultima, valor=v,
                 referencia=ref.valor, impuestos_eur=CAPITAL_EUR * r.impuestos)


def nuevas(hoy: Papel, ayer_hasta: pd.Timestamp | None) -> list[Operacion]:
    """Operaciones ejecutadas despues del dia del ultimo papel (para avisar solo de las nuevas)."""
    return [o for o in hoy.operaciones if ayer_hasta is None or o.fecha > ayer_hasta]


def revision(cierres: pd.DataFrame, senyal: pd.Timestamp, primera: pd.Timestamp) -> dict:
    """Lo que decide la senyal de un mes (se ejecuta el dia habil siguiente): pesos nuevos, los de antes, compras,
    ventas y puntos. Antes de la primera senyal del papel no habia nada (todo en el monetario)."""
    piezas = piezas_de(cierres).loc[:senyal]
    objetivo = E.pesos_objetivo(piezas, H1M)
    nuevo = {p: float(objetivo.loc[senyal, p]) for p in PIEZAS}
    previas = objetivo.loc[(objetivo.index < senyal) & (objetivo.index >= primera)]
    anterior = {p: float(previas.iloc[-1][p]) for p in PIEZAS} if senyal > primera and len(previas) else dict.fromkeys(PIEZAS, 0.0)
    return {"senyal": senyal.date().isoformat(), "pesos_nuevos": nuevo, "pesos_antes": anterior,
            "compras": [p for p in PIEZAS if nuevo[p] > anterior[p] + 1e-12],
            "ventas": [p for p in PIEZAS if nuevo[p] < anterior[p] - 1e-12],
            "puntos": {p: int(E.medias_superadas(piezas[p]).loc[senyal]) for p in PIEZAS}}
