"""Operaciones del estudio 3 (docs/plan-estudio-3.md): senyal, tres barreras, reglas fijas, costes y escenarios.

Lo usan el diagnostico y, mas adelante, la exploracion. No mide nada por si solo.

Datos: velas de 1 hora de Dukascopy (compra y venta). Un "dia" va de 17:00 a 17:00 de Nueva York y lleva la fecha
de su final (como en el estudio 1).

Senyal (T17, P2), por par y dia, con los niveles del dia anterior:
- compra si el ask baja al menos 1 pip por debajo del minimo de ayer (del ask); se llena al minimo de ayer;
- venta si el bid sube al menos 1 pip por encima del maximo de ayer (del bid); se llena al maximo de ayer.
Una posicion por par (F5); la primera senyal del dia (por horas); como mucho una entrada por par y dia.
No se abre entre las 16:00 y las 18:00 de Nueva York, del 24/12 al 2/1 (T3), ni el viernes desde las 16:00 (P3).

Salidas (triple-barrier, con la regla prudente):
- objetivo: la mitad del rango de ayer (en precios medios); la compra vende al tocarlo el bid, la venta al tocarlo el ask;
- stop: k rangos medios (20 dias, hasta ayer) en contra de la entrada; se ejecuta 1 diferencial peor, o a la apertura
  de la hora si esta ya abre mas alla (F10);
- en la misma hora, si se tocan stop y objetivo, cuenta el stop; en la hora de entrada solo cuenta el stop;
- limite de tiempo: al cierre de la hora de las 15:00 de Nueva York del ultimo dia permitido;
- el viernes, todo se cierra al cierre de la hora de las 15:00 de Nueva York (P3).

Costes (por operacion, en fraccion del nominal): comision de 35 $ por millon y lado (Dukascopy), intereses de cada
noche (diferencia de tipos oficiales menos un recargo prudente del 1,5 % al anyo; el miercoles cuenta 3 noches, T10)
y 0,1 % del resultado al pasarlo a euros (F12). El diferencial ya va en los precios de compra y venta.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DUKAS = RAIZ / "var" / "estudio1" / "dukascopy"
COMISION = 35 / 1e6
RECARGO = 1.5  # % al anyo sobre los intereses de cada noche (no publico; prudente)
CONVERSION = 0.001
NY = "America/New_York"


@dataclass(frozen=True)
class Barreras:
    k_stop: float = 1.0
    max_dias: int = 5


def pip(par: str) -> float:
    return 0.01 if par.endswith("JPY") else 0.0001


def preparar_horas(h: pd.DataFrame) -> pd.DataFrame:
    """Anyade la hora de Nueva York y el dia (17:00 a 17:00, con la fecha de su final)."""
    h = h.copy()
    ny = h.index.tz_convert(NY)
    h["hora_ny"] = ny.hour
    h["dow_ny"] = ny.dayofweek
    h["dia"] = pd.DatetimeIndex((ny + pd.Timedelta(hours=7)).date)
    return h


def dias_de_horas(h: pd.DataFrame) -> pd.DataFrame:
    g = h.groupby("dia")
    d = pd.DataFrame({
        "ask_l": g["ask_l"].min(), "bid_h": g["bid_h"].max(),
        "mid_h": g.apply(lambda x: ((x["bid_h"] + x["ask_h"]) / 2).max(), include_groups=False),
        "mid_l": g.apply(lambda x: ((x["bid_l"] + x["ask_l"]) / 2).min(), include_groups=False),
        "mid_c": g.apply(lambda x: (x["bid_c"].iloc[-1] + x["ask_c"].iloc[-1]) / 2, include_groups=False),
    })
    d["rango"] = d["mid_h"] - d["mid_l"]
    # Todo lo que se usa el dia d sale de dias anteriores (shift): nada del futuro (ml4t-data-leakage).
    d["ayer_ask_l"] = d["ask_l"].shift(1)
    d["ayer_bid_h"] = d["bid_h"].shift(1)
    d["objetivo"] = ((d["mid_h"] + d["mid_l"]) / 2).shift(1)
    d["rango_medio"] = d["rango"].shift(1).rolling(20, min_periods=20).mean()
    d["min20"] = d["ask_l"].shift(1).rolling(20, min_periods=20).min()
    d["max20"] = d["bid_h"].shift(1).rolling(20, min_periods=20).max()
    media200 = d["mid_c"].shift(1).rolling(200, min_periods=200).mean()
    d["media200"] = media200
    d["pendiente200"] = media200 - media200.shift(20)
    d["cierre_ayer"] = d["mid_c"].shift(1)
    d["rango_ayer"] = d["rango"].shift(1)
    d["rango_medio_previo"] = d["rango"].shift(2).rolling(20, min_periods=20).mean()
    return d


def puede_abrir(hora_ny: int, dow_ny: int, ts_ny: pd.Timestamp) -> bool:
    if 16 <= hora_ny < 18:
        return False
    if dow_ny == 4 and hora_ny >= 16:
        return False
    if (ts_ny.month == 12 and ts_ny.day >= 24) or (ts_ny.month == 1 and ts_ny.day <= 2):
        return False
    return True


def preparar_tipos(tipos: pd.DataFrame) -> pd.DataFrame:
    """Tipos oficiales por dia natural: se arrastra el ultimo hasta 31 dias; donde no hay tipo oficial (Japon
    2001-2006 y 2013-2016, politica por cantidad de dinero) se usa 0 %."""
    dias = pd.date_range(tipos.index.min(), tipos.index.max(), freq="D")
    return tipos.reindex(dias).ffill(limit=31).fillna(0.0)


def interes_diario(tipos: pd.DataFrame, base: str, cotizada: str, sentido: int, dia: pd.Timestamp) -> float:
    """Interes de una noche, en fraccion del nominal (tipos ya preparados). La compra cobra el tipo de la base y paga
    el de la cotizada; la venta, al reves; siempre menos el recargo del broker."""
    fila = tipos.loc[min(dia, tipos.index[-1])]
    return (sentido * (float(fila[base]) - float(fila[cotizada])) - RECARGO) / 100 / 365


def operaciones(h: pd.DataFrame, par: str, tipos: pd.DataFrame, b: Barreras) -> pd.DataFrame:
    """Todas las operaciones del par con las reglas fijas. h: velas de 1 hora ya preparadas (preparar_horas)."""
    d = dias_de_horas(h)
    p = pip(par)
    base, cotizada = par[:3], par[3:]
    cols = {c: h[c].to_numpy() for c in ("bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c",
                                          "hora_ny", "dow_ny")}
    dia_arr = h["dia"].to_numpy()
    idx_ny = h.index.tz_convert(NY)
    dias = list(d.index)
    pos_dia = {x: i for i, x in enumerate(dias)}
    inicio_de_dia = {}
    for i, x in enumerate(dia_arr):
        inicio_de_dia.setdefault(pd.Timestamp(x), i)
    out = []
    libre_desde = 0  # primera hora en que el par vuelve a estar libre
    for di, dia in enumerate(dias):
        fila = d.iloc[di]
        if np.isnan(fila["rango_medio"]) or np.isnan(fila["ayer_ask_l"]):
            continue
        i0 = inicio_de_dia[dia]
        i_fin = inicio_de_dia[dias[di + 1]] if di + 1 < len(dias) else len(dia_arr)
        entrada = None
        for i in range(max(i0, libre_desde), i_fin):
            if not puede_abrir(cols["hora_ny"][i], cols["dow_ny"][i], idx_ny[i]):
                continue
            if cols["ask_l"][i] <= fila["ayer_ask_l"] - p:
                entrada = (i, 1, fila["ayer_ask_l"])
                break
            if cols["bid_h"][i] >= fila["ayer_bid_h"] + p:
                entrada = (i, -1, fila["ayer_bid_h"])
                break
        if entrada is None:
            continue
        i, s, precio = entrada
        objetivo = fila["objetivo"]
        if s * (objetivo - precio) <= 0:  # el objetivo ya esta del lado malo: no es una senyal
            continue
        stop = precio - s * b.k_stop * fila["rango_medio"]
        ultimo_dia = dias[min(di + b.max_dias, len(dias) - 1)]
        salida, motivo, j = None, None, i
        while j < len(dia_arr):
            spread = cols["ask_c"][j] - cols["bid_c"][j]
            if s == 1:
                abre_mas_alla = j > i and cols["bid_o"][j] <= stop
                toca_stop = cols["bid_l"][j] <= stop
                toca_obj = j > i and cols["bid_h"][j] >= objetivo
            else:
                abre_mas_alla = j > i and cols["ask_o"][j] >= stop
                toca_stop = cols["ask_h"][j] >= stop
                toca_obj = j > i and cols["ask_l"][j] <= objetivo
            if toca_stop:
                apertura = cols["bid_o"][j] if s == 1 else cols["ask_o"][j]
                salida, motivo = (apertura if abre_mas_alla else stop - s * spread), "stop"
                break
            if toca_obj:
                salida, motivo = objetivo, "objetivo"
                break
            dia_j = pd.Timestamp(dia_arr[j])
            if cols["hora_ny"][j] == 15 and (cols["dow_ny"][j] == 4 or dia_j >= ultimo_dia):
                salida = cols["bid_c"][j] if s == 1 else cols["ask_c"][j]
                motivo = "viernes" if cols["dow_ny"][j] == 4 else "tiempo"
                break
            if dia_j > ultimo_dia:  # no hubo hora de las 15:00 (hueco): se cierra en la primera hora posterior
                salida, motivo = (cols["bid_o"][j] if s == 1 else cols["ask_o"][j]), "tiempo"
                break
            j += 1
        if salida is None:
            break  # fin de los datos con la posicion abierta: se descarta
        bruto = s * (salida - precio) / precio
        # noches: cambios de dia entre la entrada y la salida; la noche del miercoles al jueves cuenta 3 (T10)
        dia_e, dia_s = pd.Timestamp(dia_arr[i]), pd.Timestamp(dia_arr[j])
        noches = 0.0
        for k in range(pos_dia[dia_e], pos_dia[dia_s]):
            n = 3 if dias[k].dayofweek == 2 else 1
            noches += n * interes_diario(tipos, base, cotizada, s, dias[k])
        neto = bruto - 2 * COMISION + noches - CONVERSION * abs(bruto)
        out.append({"par": par, "dia": dia, "sentido": s, "entrada": precio, "hora_entrada": h.index[i],
                    "salida": salida, "hora_salida": h.index[j], "motivo": motivo, "bruto": bruto,
                    "intereses": noches, "neto": neto})
        libre_desde = j + 1
    return pd.DataFrame(out)


def marcar(ops: pd.DataFrame, d: pd.DataFrame, h: pd.DataFrame, eventos: pd.DataFrame, vix: pd.Series,
           par: str) -> pd.DataFrame:
    """Escenarios del diagnostico (plan, seccion 4), todos con datos de antes de entrar."""
    ops = ops.copy()
    divisas = {par[:3], par[3:]}
    fechas_ev = set(pd.to_datetime(eventos.loc[eventos["divisa"].isin(divisas) | (eventos["evento"] == "Empleo EE. UU."),
                                               "fecha"]))
    dias = list(d.index)
    pos = {x: i for i, x in enumerate(dias)}
    vix_pct = vix.rolling(252, min_periods=200).apply(lambda x: (x <= x[-1]).mean(), raw=True)
    m1, m2, m3, m4, m5 = [], [], [], [], []
    for _, o in ops.iterrows():
        dia, s = o["dia"], o["sentido"]
        fila = d.loc[dia]
        anterior = dias[pos[dia] - 1] if pos[dia] > 0 else dia
        # 1. evento ese dia o el anterior (fecha local del evento; un fin de semana cuenta para el lunes)
        ev_dias = {dia, anterior}
        m1.append(any(x in fechas_ev or (x.dayofweek == 0 and (x - pd.Timedelta(days=1) in fechas_ev
                                                                  or x - pd.Timedelta(days=2) in fechas_ev))
                      for x in ev_dias))
        # 2. tendencia en contra
        if s == 1:
            m2.append(bool(fila["cierre_ayer"] < fila["media200"] and fila["pendiente200"] < 0))
        else:
            m2.append(bool(fila["cierre_ayer"] > fila["media200"] and fila["pendiente200"] > 0))
        # 3. volatilidad disparada
        m3.append(bool(fila["rango_ayer"] > 2 * fila["rango_medio_previo"]))
        # 4. huida del riesgo: VIX del ultimo cierre anterior al dia de entrada en el 10 % mas alto de su anyo
        v = vix_pct.loc[:dia - pd.Timedelta(days=1)].dropna()
        m4.append(bool(len(v) and v.iloc[-1] >= 0.9))
        # 5. rotura del minimo (maximo) de 20 sesiones en la hora de entrada
        hh = h.loc[o["hora_entrada"]]
        m5.append(bool(hh["ask_l"] <= fila["min20"]) if s == 1 else bool(hh["bid_h"] >= fila["max20"]))
    ops["evento"], ops["tendencia"], ops["volatilidad"], ops["miedo"], ops["rotura"] = m1, m2, m3, m4, m5
    ops["marcada"] = ops[["evento", "tendencia", "volatilidad", "miedo", "rotura"]].any(axis=1)
    return ops


def juzgar(ops: pd.DataFrame) -> dict:
    """Puerta del diagnostico (plan, seccion 4, opcion A del propietario)."""
    n = len(ops)
    limpias = ops[~ops["marcada"]]
    corte = ops["neto"].quantile(0.05)
    peores = ops[ops["neto"] <= corte]
    c1 = len(limpias) > 0 and limpias["neto"].mean() > 0
    c2 = n > 0 and len(limpias) / n >= 0.40
    c3 = len(peores) > 0 and peores["marcada"].mean() >= 0.5
    return {"operaciones": n, "no_marcadas": len(limpias), "media_no_marcadas": float(limpias["neto"].mean()),
            "mediana_no_marcadas": float(limpias["neto"].median()), "media_todas": float(ops["neto"].mean()),
            "parte_no_marcadas": len(limpias) / n if n else 0.0, "peores_marcadas": float(peores["marcada"].mean()),
            "condiciones": {"1. las no marcadas ganan de media": bool(c1),
                            "2. quedan al menos el 40 %": bool(c2),
                            "3. las marcadas tienen al menos la mitad de las peores": bool(c3)},
            "pasa": bool(c1 and c2 and c3)}
