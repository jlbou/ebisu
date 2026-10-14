"""Estrategia del bot en papel: COPIA EXACTA de estudios/estudio4/simulador4.py (docs/plan-bot-papel.md 4 y 10, B1).

No se cambia la logica: una prueba (tests/test_bot_estrategia.py) compara este fichero con el del estudio, salvo este
texto de cabecera. La huella de este fichero se guarda el primer dia del papel; si cambia durante el papel, es una
incidencia (decision 11.2.1).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

MEDIAS = (20, 50, 100, 200)
DOS_MESES = pd.Timedelta(days=61)
TRAMOS = ((6_000, 0.19), (50_000, 0.21), (200_000, 0.23), (300_000, 0.27), (float("inf"), 0.30))
CAPITAL = 250.0  # euros iniciales: los tramos se aplican a euros, no a "por euro"
VOL_DIAS, VOL_MAX, VOL_MIN = 63, 2520, 504


def cuota(base: float) -> float:
    """Impuesto del ahorro (estatal + autonomico) para una base en euros."""
    imp, desde = 0.0, 0.0
    for hasta, tipo in TRAMOS:
        if base <= desde:
            break
        imp += (min(base, hasta) - desde) * tipo
        desde = hasta
    return imp


@dataclass(frozen=True)
class Variante:
    nombre: str
    fondos: bool = False
    piezas: tuple[str, ...] = ("bolsa", "bonos", "oro")
    coste_lado: float = 0.0010
    gasto_extra: dict = field(default_factory=dict)
    retraso: int = 1
    capa2: bool = False
    capa3: bool = False
    multiplicador: pd.Series | None = None  # capa 6: factor (1 o 0,5) para la bolsa por dia de senyal
    impuestos: bool = True
    calendario: dict | None = None  # solo para validar: {fecha: {pieza: peso}}


def medias_superadas(serie: pd.Series) -> pd.Series:
    n = sum((serie > serie.rolling(m, min_periods=m).mean()).astype(int) for m in MEDIAS)
    return n.where(serie.rolling(max(MEDIAS), min_periods=max(MEDIAS)).count() == max(MEDIAS))


def dias_de_senyal(fechas: pd.DatetimeIndex) -> pd.DatetimeIndex:
    s = fechas.to_series()
    return pd.DatetimeIndex(s.groupby(s.dt.to_period("M")).max().to_numpy())


def factor_volatilidad(serie: pd.Series) -> pd.Series:
    """Capa 2: min(1, vol. objetivo / vol. de 63 dias); objetivo = mediana de la vol. de 63 dias de los hasta 10 anyos
    anteriores (minimo 2 anyos de historia; antes, 1). Todo con datos hasta el dia (incluido) de la senyal."""
    vol = serie.pct_change().rolling(VOL_DIAS, min_periods=VOL_DIAS).std()
    objetivo = vol.shift(1).rolling(VOL_MAX, min_periods=VOL_MIN).median()
    return (objetivo / vol).clip(upper=1.0).fillna(1.0)


def cuartos_fiscales(cuenta: pd.Series) -> pd.Series:
    """Capa 3: una pieza solo se reduce si su senyal baja 2 cuartos o mas, o llega a 0; las subidas, siempre."""
    out, actual = [], None
    for n in cuenta:
        if np.isnan(n):
            out.append(np.nan)
            continue
        if actual is None or n > actual or n == 0 or actual - n >= 2:
            actual = n
        out.append(actual)
    return pd.Series(out, index=cuenta.index)


def pesos_objetivo(piezas: pd.DataFrame, v: Variante) -> pd.DataFrame:
    """Peso objetivo de cada pieza en cada dia de senyal (sin el monetario)."""
    parte = 1 / len(v.piezas)
    senyales = dias_de_senyal(piezas.index)
    cuenta = pd.DataFrame({p: medias_superadas(piezas[p]).reindex(senyales) for p in v.piezas})
    cuenta = cuenta.dropna()
    if v.capa3:
        cuenta = cuenta.apply(cuartos_fiscales)
    pesos = parte * cuenta / 4
    if v.capa2:
        for p in v.piezas:
            pesos[p] *= factor_volatilidad(piezas[p]).reindex(pesos.index).to_numpy()
    if v.multiplicador is not None and "bolsa" in pesos:
        pesos["bolsa"] *= v.multiplicador.reindex(pesos.index).fillna(1.0).to_numpy()
    return pesos


@dataclass
class Resultado:
    valor: pd.Series  # valor diario por euro inicial (impuestos ya pagados restados)
    bolsillo: float  # lo que queda tras venderlo todo y pagar lo pendiente, por euro inicial
    impuestos: float
    costes: float
    operaciones: int


def simular(piezas: pd.DataFrame, v: Variante, inicio: str, fin: str) -> Resultado:
    tramo = piezas.loc[inicio:fin]
    fechas = tramo.index
    activos = list(v.piezas) + ["monetario"]
    objetivo = pesos_objetivo(piezas.loc[:fin], v)
    pos = piezas.index
    ejec = {}
    for d, fila in objetivo.iterrows():
        i = pos.get_loc(d) + v.retraso
        if i < len(pos) and pd.Timestamp(inicio) <= pos[i] <= pd.Timestamp(fin):
            ejec[pos[i]] = fila
    if v.calendario is not None:
        ejec = {pd.Timestamp(f): pd.Series(w) for f, w in v.calendario.items()}
    elif fechas[0] not in ejec:
        previas = objetivo.loc[: fechas[0]]
        if len(previas):
            ejec[fechas[0]] = previas.iloc[-1]  # arranca con la ultima senyal conocida

    precios = tramo[activos]
    gasto_anual = np.array([v.gasto_extra.get(a, 0.0) for a in activos])
    dias_nat = fechas.to_series().diff().dt.days.fillna(0).to_numpy()  # gasto por dias naturales / 365
    unidades = dict.fromkeys(activos, 0.0)
    unidades["monetario"] = (1.0 - v.coste_lado) / precios["monetario"].iloc[0]
    lotes = {a: deque() for a in activos}
    lotes["monetario"].append((fechas[0], unidades["monetario"], 1.0 / unidades["monetario"]))
    aplazada = dict.fromkeys(activos, 0.0)
    arrastre = deque()
    neto_anyo, pagado, costes, ops, peso_actual = 0.0, 0.0, v.coste_lado, 0, {}
    perdidas = {a: [] for a in activos}
    valores = []
    con_impuestos = v.impuestos and not v.fondos

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
        if v.fondos:
            return
        for reg in perdidas[a]:
            if reg[1] < 0 and pd.Timedelta(0) < d - reg[0] <= DOS_MESES:
                neto_anyo -= reg[1]
                aplazada[a] += reg[1]
                reg[1] = 0.0

    def pagar_anyo(anyo):
        """Impuesto del anyo por euro inicial: base neta (en euros = x CAPITAL) por los tramos."""
        nonlocal neto_anyo
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
        return cuota(base * CAPITAL) / CAPITAL

    for k, d in enumerate(fechas):
        p = precios.loc[d]
        if k > 0:
            gasto = gasto_anual * dias_nat[k] / 365
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
                caja = -delta * p[a] - coste
                c2 = abs(caja) * v.coste_lado
                costes += c2
                dm = (caja - c2) / p["monetario"]
                if dm > 0:
                    comprar("monetario", dm, d, p["monetario"])
                elif dm < 0:
                    vender("monetario", -dm, d, p["monetario"])
                unidades["monetario"] += dm
        es_fin_anyo = k + 1 < len(fechas) and fechas[k + 1].year != d.year
        if es_fin_anyo and con_impuestos:
            imp = pagar_anyo(d.year)
            if imp:
                pagado += imp
                vender("monetario", imp / p["monetario"], d, p["monetario"])
                unidades["monetario"] -= imp / p["monetario"]
        valores.append(sum(unidades[a] * p[a] for a in activos))

    d, p = fechas[-1], precios.iloc[-1]
    bruto = valores[-1]
    salida = sum(unidades[a] * p[a] for a in activos) * v.coste_lado
    for a in activos:
        if unidades[a] > 0:
            vender(a, unidades[a], d, p[a])
            if aplazada[a]:
                neto_anyo += aplazada[a]
                aplazada[a] = 0.0
    if not v.impuestos:
        imp = 0.0
    elif v.fondos:
        imp = cuota(max(bruto - salida - 1.0, 0.0) * CAPITAL) / CAPITAL
    else:
        imp = pagar_anyo(d.year)
    pagado += imp
    return Resultado(pd.Series(valores, index=fechas), bruto - salida - imp, pagado, costes + salida, ops)


def referencia(piezas: pd.DataFrame, inicio: str, fin: str, gasto: float = 0.0015, impuestos: bool = True) -> Resultado:
    """La pieza de bolsa en un fondo indexado mantenido: sin operar, impuesto al final con los tramos."""
    b = piezas["bolsa"].loc[inicio:fin]
    dias = b.index.to_series().diff().dt.days.fillna(0).to_numpy()
    valor = (b / b.iloc[0]) * pd.Series(np.cumprod(1 - gasto * dias / 365), index=b.index)
    imp = cuota(max(valor.iloc[-1] - 1.0, 0.0) * CAPITAL) / CAPITAL if impuestos else 0.0
    return Resultado(valor, valor.iloc[-1] - imp, imp, 0.0, 0)
