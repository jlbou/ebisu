"""Capa 6 del estudio 4 (docs/plan-estudio-4.md 5): cuando la tendencia dice "dentro", ¿acertara el mes que viene?

- Aprende de los 49 sectores de EE. UU. (Kenneth French, mensuales, ponderados por valor). Muestra: cada sector y mes t
  con nivel por encima de su media de 10 meses; etiqueta = 1 si en t+1 gana mas que las letras del Tesoro.
- Variables en t (solo datos hasta t): volatilidad de 3 y 12 meses; distancia a la media de 10 meses en unidades de la
  volatilidad de 12; cuantos de los rendimientos de 1, 3, 6 y 12 meses son positivos; porcentaje de sectores por
  encima de su media; inflacion de EE. UU. a 12 meses de t-2 (CPIAUCNS).
- Regresion logistica (C = 1) en un Pipeline con la normalizacion. Un modelo por anyo Y, entrenado con las muestras cuya
  etiqueta acaba como muy tarde el 31/12 del anyo Y-2 (12 meses de separacion antes de usarlo en enero de Y).
- Se aplica a la pieza de bolsa EN DOLARES: probabilidad < 0,5 -> su peso se reduce a la mitad.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[2]
F = RAIZ / "var" / "estudio4" / "fuentes"
VARIABLES = ["vol3", "vol12", "distancia", "plazos_positivos", "amplitud", "inflacion"]


def sectores() -> pd.DataFrame:
    """Rendimientos mensuales (en tanto por uno) del primer bloque: ponderados por valor."""
    lineas = (F / "french_49_sectores" / "49_Industry_Portfolios.csv").read_text().splitlines()
    i = next(k for k, ln in enumerate(lineas) if "Average Value Weighted Returns -- Monthly" in ln)
    cab = [c.strip() for c in lineas[i + 1].split(",")][1:]
    filas = {}
    for ln in lineas[i + 2:]:
        partes = [c.strip() for c in ln.split(",")]
        if not re.fullmatch(r"\d{6}", partes[0]):
            break
        filas[partes[0]] = [float(x) for x in partes[1:]]
    df = pd.DataFrame.from_dict(filas, orient="index", columns=cab).replace([-99.99, -999], np.nan) / 100
    df.index = pd.to_datetime(df.index, format="%Y%m") + pd.offsets.MonthEnd(0)
    return df


def letras_mensuales() -> pd.Series:
    lineas = (F / "french_mensual" / "F-F_Research_Data_Factors.csv").read_text().splitlines()
    filas = {}
    for ln in lineas:
        partes = [c.strip() for c in ln.split(",")]
        if re.fullmatch(r"\d{6}", partes[0]):
            filas[partes[0]] = float(partes[4]) / 100
        elif filas:
            break
    s = pd.Series(filas)
    s.index = pd.to_datetime(s.index, format="%Y%m") + pd.offsets.MonthEnd(0)
    return s


def inflacion() -> pd.Series:
    """Inflacion a 12 meses de t-2 (lo publicado al cierre del mes t)."""
    c = pd.read_csv(F / "fred_CPIAUCNS.csv", index_col=0, parse_dates=True).iloc[:, 0].astype(float)
    c.index = c.index + pd.offsets.MonthEnd(0)
    return (c / c.shift(12) - 1).shift(2)


def variables_de(rend: pd.Series) -> pd.DataFrame:
    """Variables de una serie de rendimientos mensuales, con datos hasta cada mes (incluido)."""
    nivel = (1 + rend.fillna(0)).cumprod().where(rend.notna())
    media10 = nivel.rolling(10, min_periods=10).mean()
    vol12 = rend.rolling(12, min_periods=12).std()
    plazos = sum((nivel / nivel.shift(k) - 1 > 0).astype(float).where(nivel.shift(k).notna()) for k in (1, 3, 6, 12))
    return pd.DataFrame({"vol3": rend.rolling(3, min_periods=3).std(), "vol12": vol12,
                         "distancia": (nivel / media10 - 1) / vol12, "plazos_positivos": plazos,
                         "encima": (nivel > media10).where(media10.notna())})


def panel(sec: pd.DataFrame, rf: pd.Series, infl: pd.Series) -> pd.DataFrame:
    """Muestras de los sectores con senyal "dentro" en t; etiqueta con t+1."""
    por_sector = {c: variables_de(sec[c]) for c in sec.columns}
    amplitud = pd.DataFrame({c: v["encima"] for c, v in por_sector.items()}).mean(axis=1)
    trozos = []
    for c, v in por_sector.items():
        d = v.copy()
        d["amplitud"] = amplitud
        d["inflacion"] = infl.reindex(d.index)
        d["etiqueta"] = (sec[c].shift(-1) > rf.reindex(sec.index).shift(-1)).astype(float)
        d["etiqueta"] = d["etiqueta"].where(sec[c].shift(-1).notna())
        d["fin_etiqueta"] = d.index.to_series().shift(-1)
        d = d[d["encima"] == 1.0].dropna(subset=VARIABLES + ["etiqueta"])
        d["sector"] = c
        trozos.append(d)
    return pd.concat(trozos).sort_index()


def nuevo_modelo() -> Pipeline:
    return Pipeline([("norma", StandardScaler()), ("logistica", LogisticRegression(C=1.0, max_iter=1000))])


def probabilidades(muestras: pd.DataFrame, aplicar: pd.DataFrame, anyos: range) -> tuple[pd.Series, pd.DataFrame]:
    """Probabilidad para cada fila de `aplicar` (indice = fin de mes), con el modelo de su anyo; y los coeficientes
    normalizados de cada modelo (para la importancia)."""
    probs, coefs = {}, {}
    for y in anyos:
        filas = aplicar[aplicar.index.year == y]
        if filas.empty:
            continue
        ent = muestras[muestras["fin_etiqueta"] <= pd.Timestamp(f"{y - 2}-12-31")]
        modelo = nuevo_modelo().fit(ent[VARIABLES], ent["etiqueta"].astype(int))
        coefs[y] = np.abs(modelo.named_steps["logistica"].coef_[0])
        ok = filas[VARIABLES].notna().all(axis=1)
        p = pd.Series(np.nan, index=filas.index)
        if ok.any():
            p[ok] = modelo.predict_proba(filas.loc[ok, VARIABLES])[:, 1]
        probs.update(p.to_dict())
    return pd.Series(probs).sort_index(), pd.DataFrame.from_dict(coefs, orient="index", columns=VARIABLES)


def importancia_maxima(coefs: pd.DataFrame) -> float:
    """Parte de la importancia (|coeficiente normalizado| medio) que se lleva la variable mas importante."""
    media = coefs.mean()
    return float(media.max() / media.sum())


def multiplicador(bolsa_usd: pd.Series, dias_senyal: pd.DatetimeIndex, anyos: range, sec: pd.DataFrame,
                  rf: pd.Series, infl: pd.Series) -> tuple[pd.Series, float]:
    """Factor (1 o 0,5) para la pieza de bolsa en cada dia de senyal, y la importancia maxima."""
    muestras = panel(sec, rf, infl)
    amplitud = pd.DataFrame({c: variables_de(sec[c])["encima"] for c in sec.columns}).mean(axis=1)
    mensual = bolsa_usd.resample("ME").last().pct_change()
    v = variables_de(mensual)
    v["amplitud"] = amplitud.reindex(v.index)
    v["inflacion"] = infl.reindex(v.index)
    p, coefs = probabilidades(muestras, v, anyos)
    clave = dias_senyal.to_period("M").to_timestamp("M")
    factor = np.where(p.reindex(clave).to_numpy() < 0.5, 0.5, 1.0)
    return pd.Series(factor, index=dias_senyal), importancia_maxima(coefs)


def sin_futuro(funcion, rend: pd.Series, cortes: list[pd.Timestamp]) -> bool:
    """True si la variable en cada corte sale igual con la serie cortada en ese mes (no mira el futuro)."""
    entera = funcion(rend)
    for c in cortes:
        cortada = funcion(rend.loc[:c])
        a, b = entera.loc[c], cortada.loc[c]
        if not np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float), equal_nan=True):
            return False
    return True
