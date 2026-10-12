"""Simulador de H1 (docs/diseno-estudio-1.md, secciones 3-6). No mide nada por si solo: lo usan el validador y el juez.

Modelo (lo fijado en el criterio, sin anyadir nada):
- Piezas: indices diarios en euros (montar_series.py). Senyal sobre ese mismo indice: cuantas de sus medias de 20, 50,
  100 y 200 dias estan por debajo del precio (0 a 4).
- Peso objetivo: escalonado = parte x (medias superadas / 4); todo o nada = parte si >= 2 de 4. La parte es 1/3 (ETF:
  bolsa, bonos y oro) o 1/2 (fondos: bolsa y bonos). Lo que sobra, al monetario.
- Senyal el ultimo dia habil del mes (o de la semana); se ejecuta al cierre del dia habil siguiente (fondos: 6 dias
  habiles despues). Solo se tocan las piezas cuyo peso objetivo cambia; el monetario absorbe la diferencia.
- Costes: ETF, 0,10 % por lado sobre lo que se compra o vende (monetario incluido); gasto anual extra a diario.
- Impuestos (19 %): ETF, por lotes FIFO; ganancias y perdidas del anyo se compensan, la perdida neta se arrastra 4
  anyos; regla de los dos meses (una perdida no cuenta si se compra la misma pieza 2 meses antes o despues: se aplaza
  hasta que la pieza se vende entera); el impuesto del anyo se paga el ultimo dia habil del anyo. Fondos: nada hasta el
  final. Al final del tramo se vende todo y se paga lo pendiente.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

MEDIAS = (20, 50, 100, 200)
TIPO = 0.19
DOS_MESES = pd.Timedelta(days=61)


@dataclass(frozen=True)
class Variante:
    nombre: str
    frecuencia: str = "M"  # "M" mensual, "S" semanal
    escalonada: bool = True
    fondos: bool = False
    piezas: tuple[str, ...] = ("bolsa", "bonos", "oro")
    coste_lado: float = 0.0010
    gasto_extra: dict = field(default_factory=dict)  # gasto anual extra por pieza (incluido "monetario")
    retraso: int = 1  # dias habiles entre senyal y ejecucion
    calendario: dict | None = None  # solo para validar: {fecha: {pieza: peso}} en vez de la senyal


def medias_superadas(serie: pd.Series) -> pd.Series:
    n = sum((serie > serie.rolling(m, min_periods=m).mean()).astype(int) for m in MEDIAS)
    return n.where(serie.rolling(max(MEDIAS), min_periods=max(MEDIAS)).count() == max(MEDIAS))


def dias_de_senyal(fechas: pd.DatetimeIndex, frecuencia: str) -> pd.DatetimeIndex:
    s = fechas.to_series()
    clave = s.dt.to_period("M") if frecuencia == "M" else s.dt.to_period("W-FRI")
    return pd.DatetimeIndex(s.groupby(clave).max().to_numpy())


def pesos_objetivo(piezas: pd.DataFrame, v: Variante) -> pd.DataFrame:
    """Peso objetivo de cada pieza en cada dia de senyal (sin el monetario)."""
    parte = 1 / len(v.piezas)
    filas = {}
    senyales = dias_de_senyal(piezas.index, v.frecuencia)
    cuenta = pd.DataFrame({p: medias_superadas(piezas[p]) for p in v.piezas})
    for d in senyales:
        c = cuenta.loc[d]
        if c.isna().any():
            continue
        filas[d] = {p: parte * (c[p] / 4 if v.escalonada else float(c[p] >= 2)) for p in v.piezas}
    return pd.DataFrame.from_dict(filas, orient="index")


@dataclass
class Resultado:
    valor: pd.Series  # valor diario de la cartera (impuestos ya pagados restados)
    bolsillo: float  # lo que queda tras venderlo todo y pagar lo pendiente, por euro inicial
    impuestos: float
    costes: float
    operaciones: int


def simular(piezas: pd.DataFrame, v: Variante, inicio: str, fin: str) -> Resultado:
    tramo = piezas.loc[inicio:fin]
    fechas = tramo.index
    activos = list(v.piezas) + ["monetario"]
    objetivo = pesos_objetivo(piezas.loc[:fin], v)
    # Ejecucion: v.retraso dias habiles despues de la senyal, dentro del tramo.
    pos = piezas.index
    ejec = {}
    for d, fila in objetivo.iterrows():
        i = pos.get_loc(d) + v.retraso
        if i < len(pos) and inicio <= str(pos[i].date()) <= fin:
            ejec[pos[i]] = fila
    if v.calendario is not None:
        ejec = {pd.Timestamp(f): pd.Series(w) for f, w in v.calendario.items()}
    elif fechas[0] not in ejec:
        previas = objetivo.loc[: fechas[0]]
        if len(previas):
            ejec[fechas[0]] = previas.iloc[-1]  # arranca con la ultima senyal conocida

    precios = tramo[activos]
    gasto = np.array([v.gasto_extra.get(a, 0.0) for a in activos]) / 252
    unidades = dict.fromkeys(activos, 0.0)
    unidades["monetario"] = (1.0 - v.coste_lado) / precios["monetario"].iloc[0]  # entrada al monetario
    lotes = {a: deque() for a in activos}  # (fecha, unidades, coste por unidad)
    lotes["monetario"].append((fechas[0], unidades["monetario"], 1.0 / unidades["monetario"]))
    compras = {a: [fechas[0]] if a == "monetario" else [] for a in activos}
    aplazada = dict.fromkeys(activos, 0.0)
    arrastre = deque()  # (anyo, perdida neta pendiente)
    neto_anyo, pagado, costes, ops, peso_actual = 0.0, 0.0, v.coste_lado, 0, {}
    perdidas = {a: [] for a in activos}  # ventas con perdida que cuentan: [fecha, importe, anyo]
    valores = []

    def vender(a, n, d, p):
        nonlocal neto_anyo
        resto, ganancia = n, 0.0
        while resto > 1e-15 and lotes[a]:
            fl, nl, cl = lotes[a][0]
            q = min(nl, resto)
            ganancia += q * (p * (1 - v.coste_lado) - cl)
            resto -= q
            if q >= nl - 1e-15:
                lotes[a].popleft()
            else:
                lotes[a][0] = (fl, nl - q, cl)
        if v.fondos:
            return
        # Regla de los dos meses: la perdida se aplaza si quedan en cartera unidades de la pieza compradas en los 2
        # meses anteriores (las de despues, en comprar()).
        if ganancia < 0 and any(pd.Timedelta(0) <= d - fl <= DOS_MESES for fl, _, _ in lotes[a]):
            aplazada[a] += ganancia
        else:
            neto_anyo += ganancia
            if ganancia < 0:
                perdidas[a].append([d, ganancia, d.year])
        if not lotes[a] and aplazada[a]:
            neto_anyo += aplazada[a]
            aplazada[a] = 0.0

    def comprar(a, n, d, p):
        nonlocal neto_anyo
        lotes[a].append((d, n, p * (1 + v.coste_lado)))
        compras[a].append(d)
        if v.fondos:
            return
        # Una compra en los 2 meses DESPUES de una venta con perdida tambien la aplaza (si ya se compenso en un anyo
        # cerrado, se devuelve en el anyo de la compra).
        for reg in perdidas[a]:
            if reg[1] < 0 and pd.Timedelta(0) < d - reg[0] <= DOS_MESES:
                neto_anyo -= reg[1]
                aplazada[a] += reg[1]
                reg[1] = 0.0

    def pagar_anyo(anyo):
        nonlocal neto_anyo, pagado
        base = neto_anyo
        while arrastre and arrastre[0][0] < anyo - 4:
            arrastre.popleft()
        while base > 0 and arrastre:
            a0, perd = arrastre.popleft()
            usar = min(base, -perd)
            base -= usar
            if -perd > usar:
                arrastre.appendleft((a0, perd + usar))
        if base < 0:
            arrastre.append((anyo, base))
            base = 0.0
        neto_anyo = 0.0
        return TIPO * base

    for k, d in enumerate(fechas):
        p = precios.loc[d]
        if k > 0:  # gasto extra diario
            for j, a in enumerate(activos):
                unidades[a] *= 1 - gasto[j]
                if lotes[a]:
                    lotes[a] = deque((fl, nl * (1 - gasto[j]), cl / (1 - gasto[j])) for fl, nl, cl in lotes[a])
        valor = sum(unidades[a] * p[a] for a in activos)
        if d in ejec:
            meta = ejec[d]
            cambios = []
            for a in v.piezas:
                w = float(meta.get(a, 0.0))
                if a in peso_actual and abs(peso_actual[a] - w) < 1e-12:
                    continue
                peso_actual[a] = w
                delta = w * valor / p[a] - unidades[a]
                if abs(delta) * p[a] > 1e-12:
                    cambios.append((a, delta))
            # Primero las ventas, despues las compras; una compra nunca deja el monetario en negativo.
            for a, delta in sorted(cambios, key=lambda x: x[1]):
                if delta > 0:
                    caja_disp = unidades["monetario"] * p["monetario"]
                    delta = min(delta, caja_disp / (p[a] * (1 + v.coste_lado) ** 2))
                    if delta * p[a] <= 1e-12:
                        continue
                coste = abs(delta) * p[a] * v.coste_lado
                costes += coste
                ops += 1
                if delta > 0:
                    comprar(a, delta, d, p[a])
                else:
                    vender(a, -delta, d, p[a])
                unidades[a] += delta
                caja = -delta * p[a] - coste  # lo que entra (+) o sale (-) del monetario, antes de su propio lado
                c2 = abs(caja) * v.coste_lado
                costes += c2
                dm = (caja - c2) / p["monetario"]
                if dm > 0:
                    comprar("monetario", dm, d, p["monetario"])
                elif dm < 0:
                    vender("monetario", -dm, d, p["monetario"])
                unidades["monetario"] += dm
        es_fin_anyo = k + 1 < len(fechas) and fechas[k + 1].year != d.year
        if es_fin_anyo and not v.fondos:
            imp = pagar_anyo(d.year)
            if imp:
                pagado += imp
                vender("monetario", imp / p["monetario"], d, p["monetario"])
                unidades["monetario"] -= imp / p["monetario"]
        valores.append(sum(unidades[a] * p[a] for a in activos))

    # Final del tramo: se vende todo y se paga lo pendiente.
    d, p = fechas[-1], precios.iloc[-1]
    bruto = valores[-1]
    salida = sum(unidades[a] * p[a] for a in activos) * v.coste_lado
    for a in activos:
        if unidades[a] > 0:
            vender(a, unidades[a], d, p[a])
            if aplazada[a]:
                neto_anyo += aplazada[a]
                aplazada[a] = 0.0
    if v.fondos:
        imp = TIPO * max(bruto - salida - 1.0, 0.0)
    else:
        imp = pagar_anyo(d.year)
    pagado += imp
    return Resultado(pd.Series(valores, index=fechas), bruto - salida - imp, pagado + 0.0, costes + salida, ops)


def referencia(piezas: pd.DataFrame, inicio: str, fin: str, gasto: float = 0.0) -> Resultado:
    """Indexado de bolsa mundial mantenido: sin operar, impuesto al final (fondo con traspasos)."""
    b = piezas["bolsa"].loc[inicio:fin]
    valor = (b / b.iloc[0]) * pd.Series((1 - gasto / 252) ** np.arange(len(b)), index=b.index)
    imp = TIPO * max(valor.iloc[-1] - 1.0, 0.0)
    return Resultado(valor, valor.iloc[-1] - imp, imp, 0.0, 0)
