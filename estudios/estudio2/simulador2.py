"""Simulador de E2 (docs/diseno-estudio-2.md, secciones 1-5). No mide nada por si solo: lo usan el validador y medir2.

- Senyal por activo: cuantas de sus medias de 20, 50, 100 y 200 dias estan por debajo del precio (n de 0 a 4), sobre
  el precio con repartos reinvertidos (para que un reparto no parezca una caida).
- Parte por activo, inversa a su riesgo: p_i = (1/s_i) / suma(1/s_j), s = desviacion de los rendimientos diarios de
  los ultimos 63 dias habiles. Peso objetivo w_i = p_i x n_i / 4; el resto, al monetario. Nunca mas del 100 %.
- Senyal el ultimo dia habil del mes; se ejecuta al cierre del dia habil siguiente. Una pieza solo se toca si su
  objetivo se aleja mas de 2 puntos del peso actual, o si hay que entrar (de 0) o salir (a 0) del todo.
- Costes: 0,10 % por lado (tambien en el monetario). Impuestos al 19 %: lotes FIFO (con la comision dentro), neto
  anual, perdidas arrastradas 4 anyos, regla de los dos meses; los repartos tributan al 19 % al cobrarlos y el neto
  va al monetario. Al final del tramo se vende todo y se paga lo pendiente.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np
import pandas as pd

MEDIAS = (20, 50, 100, 200)
VENTANA_VOL = 63
BANDA = 0.02
TIPO = 0.19
COSTE = 0.0010
DOS_MESES = pd.Timedelta(days=61)


def medias_superadas(serie: pd.Series) -> pd.Series:
    n = sum((serie > serie.rolling(m, min_periods=m).mean()).astype(int) for m in MEDIAS)
    return n.where(serie.rolling(max(MEDIAS), min_periods=max(MEDIAS)).count() == max(MEDIAS))


def pesos_objetivo(total: pd.DataFrame, fecha: pd.Timestamp) -> pd.Series | None:
    """Pesos de E2 con los datos hasta `fecha` (incluida). None si aun no hay historia suficiente."""
    h = total.loc[:fecha]
    if len(h) < max(MEDIAS) + 1:
        return None
    n = pd.Series({a: medias_superadas(h[a]).iloc[-1] for a in h.columns})
    s = h.pct_change().iloc[-VENTANA_VOL:].std(ddof=1)
    if n.isna().any() or s.isna().any() or (s <= 0).any():
        return None
    p = (1 / s) / (1 / s).sum()
    return p * n / 4


@dataclass
class Resultado:
    valor: pd.Series
    bolsillo: float
    impuestos: float
    costes: float
    operaciones: int
    pesos: pd.DataFrame


def simular2(precio: pd.DataFrame, total: pd.DataFrame, repartos: pd.DataFrame, monetario: pd.Series,
             inicio: str, fin: str, coste: float = COSTE, calendario: dict | None = None) -> Resultado:
    """precio: cierres reales (para operar); total: con repartos reinvertidos (para la senyal y el riesgo);
    repartos: euros por participacion pagados cada dia (0 si no); monetario: indice del monetario.
    calendario (solo para validar): {fecha: {activo: peso}} en lugar de la senyal."""
    fechas = precio.loc[inicio:fin].index
    activos = list(precio.columns)
    pos = precio.index
    ejec: dict = {}
    if calendario is not None:
        ejec = {pd.Timestamp(f): pd.Series(w).reindex(activos).fillna(0.0) for f, w in calendario.items()}
    else:
        clave = pos.to_series().dt.to_period("M")
        for d in pos.to_series().groupby(clave).max():
            i = pos.get_loc(d) + 1
            if i < len(pos) and pos[i] in fechas:
                w = pesos_objetivo(total, d)
                if w is not None:
                    ejec[pos[i]] = w
    u = dict.fromkeys(activos, 0.0)
    pm0 = monetario.loc[fechas[0]]
    um = (1 - coste) / pm0
    lotes = {a: deque() for a in activos + ["_m"]}
    lotes["_m"].append((fechas[0], um, 1.0 / um))
    aplazada = dict.fromkeys(activos + ["_m"], 0.0)
    perdidas = {a: [] for a in activos + ["_m"]}
    arrastre: deque = deque()
    neto, pagado, costes, ops = 0.0, 0.0, coste, 0
    serie, filas_pesos = [], {}

    def vender(a, n, d, p):
        nonlocal neto
        resto, g = n, 0.0
        while resto > 1e-15 and lotes[a]:
            fl, nl, cl = lotes[a][0]
            q = min(nl, resto)
            g += q * (p * (1 - coste) - cl)
            resto -= q
            if q >= nl - 1e-15:
                lotes[a].popleft()
            else:
                lotes[a][0] = (fl, nl - q, cl)
        if g < 0 and any(pd.Timedelta(0) <= d - fl <= DOS_MESES for fl, _, _ in lotes[a]):
            aplazada[a] += g
        else:
            neto += g
            if g < 0:
                perdidas[a].append([d, g])
        if not lotes[a] and aplazada[a]:
            neto += aplazada[a]
            aplazada[a] = 0.0

    def comprar(a, n, d, p):
        nonlocal neto
        lotes[a].append((d, n, p * (1 + coste)))
        for reg in perdidas[a]:
            if reg[1] < 0 and pd.Timedelta(0) < d - reg[0] <= DOS_MESES:
                neto -= reg[1]
                aplazada[a] += reg[1]
                reg[1] = 0.0

    def impuesto(anyo):
        nonlocal neto
        base = neto
        while arrastre and arrastre[0][0] < anyo - 4:
            arrastre.popleft()
        while base > 0 and arrastre:
            a0, pr = arrastre.popleft()
            usar = min(base, -pr)
            base -= usar
            if -pr > usar:
                arrastre.appendleft((a0, pr + usar))
        if base < 0:
            arrastre.append((anyo, base))
            base = 0.0
        neto = 0.0
        return TIPO * base

    def mover_monetario(caja, d, pm):
        """Entra (+) o sale (-) dinero del monetario, pagando su lado."""
        nonlocal um, costes
        c2 = abs(caja) * coste
        costes += c2
        dm = (caja - c2) / pm
        if dm > 0:
            comprar("_m", dm, d, pm)
        elif dm < 0:
            vender("_m", -dm, d, pm)
        um += dm

    for k, d in enumerate(fechas):
        p = precio.loc[d]
        pm = monetario.loc[d]
        div = repartos.loc[d] if d in repartos.index else None
        if div is not None:
            for a in activos:
                if u[a] > 0 and div[a] > 0:
                    bruto = u[a] * div[a]
                    um += bruto * (1 - TIPO) / pm  # el reparto tributa al cobrarlo; el neto al monetario
                    lotes["_m"].append((d, bruto * (1 - TIPO) / pm, pm))
                    pagado += bruto * TIPO
        valor = sum(u[a] * p[a] for a in activos) + um * pm
        if d in ejec:
            w = ejec[d]
            actual = {a: u[a] * p[a] / valor for a in activos}
            cambios = []
            for a in activos:
                obj = float(w[a])
                entra_sale = (actual[a] == 0) != (obj == 0)
                if abs(obj - actual[a]) > BANDA or (entra_sale and abs(obj - actual[a]) > 1e-12):
                    cambios.append((a, obj * valor / p[a] - u[a]))
            for a, delta in sorted(cambios, key=lambda x: x[1]):  # primero ventas
                if delta > 0:
                    delta = min(delta, um * pm / (p[a] * (1 + coste) ** 2))
                    if delta * p[a] <= 1e-12:
                        continue
                c = abs(delta) * p[a] * coste
                costes += c
                ops += 1
                if delta > 0:
                    comprar(a, delta, d, p[a])
                else:
                    vender(a, -delta, d, p[a])
                u[a] += delta
                mover_monetario(-delta * p[a] - c, d, pm)
            v2 = sum(u[a] * p[a] for a in activos) + um * pm
            filas_pesos[d] = {a: u[a] * p[a] / v2 for a in activos}
        if k + 1 < len(fechas) and fechas[k + 1].year != d.year:
            imp = impuesto(d.year)
            if imp:
                pagado += imp
                vender("_m", imp / pm, d, pm)
                um -= imp / pm
        serie.append(sum(u[a] * p[a] for a in activos) + um * pm)

    d, p, pm = fechas[-1], precio.iloc[-1], monetario.loc[fechas[-1]]
    bruto = serie[-1]
    salida = bruto * coste
    for a in activos:
        if u[a] > 0:
            vender(a, u[a], d, p[a])
    if um > 0:
        vender("_m", um, d, pm)
    for a in list(aplazada):
        neto += aplazada[a]
        aplazada[a] = 0.0
    imp = impuesto(d.year)
    pagado += imp
    return Resultado(pd.Series(serie, index=fechas), bruto - salida - imp, pagado, costes + salida, ops,
                     pd.DataFrame.from_dict(filas_pesos, orient="index"))


def referencia2(precio: pd.Series, inicio: str, fin: str) -> Resultado:
    """Indexado mundial mantenido: sin operar, todo el impuesto al final (como un fondo con traspasos)."""
    b = precio.loc[inicio:fin]
    v = b / b.iloc[0]
    imp = TIPO * max(v.iloc[-1] - 1.0, 0.0)
    return Resultado(v, v.iloc[-1] - imp, imp, 0.0, 0, pd.DataFrame())


def sinteticos(semilla: int = 5, dias: int = 1500, n: int = 4) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(semilla)
    f = pd.bdate_range("2013-01-01", periods=dias)
    vol = np.linspace(0.004, 0.02, n)
    precio = pd.DataFrame({f"a{i}": 100 * np.exp(np.cumsum(rng.normal(0.0002, vol[i], dias))) for i in range(n)}, index=f)
    repartos = pd.DataFrame(0.0, index=f, columns=precio.columns)
    mon = pd.Series(100 * np.cumprod(np.full(dias, 1.00005)), index=f)
    return precio, precio.copy(), repartos, mon

