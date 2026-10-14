"""Juez del estudio 4 (docs/plan-estudio-4.md 7): aplica las condiciones y nadie lo interpreta.

- TAE despues de impuestos (bolsillo ^ (1 / anyos) - 1) y caida maxima con el valor diario (impuestos ya pagados
  restados; la referencia, sin su impuesto pendiente).
- Sharpe con rendimientos MENSUALES sobre el monetario, antes de impuestos; deflactado (Bailey y Lopez de Prado) con
  asimetria y colas, N = 10 y la varianza de los Sharpe de las 5 variantes (o la de pura suerte, 1 / meses, si es mayor).
- Tipos de mercado: por anyos naturales completos, rendimientos antes de impuestos.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np
import pandas as pd

N_INTENTOS = 10
EULER = 0.5772156649015329
LISTON_DSR = 0.95
TOLERANCIA_TAE = 0.01
FRACCION_CAIDA = 2 / 3
DETRAS_SUBIDA = -0.05
INFLACION_ALTA = 0.04
MIN_ANYOS_TIPO = 3
Z = NormalDist()


@dataclass
class Metricas:
    tae: float
    caida: float
    sharpe: float  # anual (mensual x raiz de 12)
    sharpe_mensual: float
    asimetria: float
    curtosis: float  # no en exceso (normal = 3)
    meses: int


def tae(bolsillo: float, valor: pd.Series) -> float:
    anyos = (valor.index[-1] - valor.index[0]).total_seconds() / 86400 / 365.25
    return bolsillo ** (1 / anyos) - 1


def caida(valor: pd.Series) -> float:
    return float((1 - valor / valor.cummax()).max())


def exceso_mensual(valor: pd.Series, monetario: pd.Series) -> pd.Series:
    v = valor.resample("ME").last()
    m = monetario.reindex(valor.index).resample("ME").last()
    return (v.pct_change() - m.pct_change()).dropna()


def metricas(valor_con: pd.Series, bolsillo: float, valor_sin: pd.Series, monetario: pd.Series) -> Metricas:
    ex = exceso_mensual(valor_sin, monetario)
    sd = float(ex.std(ddof=1))
    sr = float(ex.mean()) / sd if sd > 0 else 0.0
    return Metricas(tae(bolsillo, valor_con), caida(valor_con), sr * math.sqrt(12), sr, float(ex.skew()),
                    float(ex.kurt()) + 3.0, len(ex))


def sharpe_umbral(varianza_sr: float, n: int) -> float:
    if n <= 1:
        return 0.0
    return math.sqrt(varianza_sr) * ((1 - EULER) * Z.inv_cdf(1 - 1 / n) + EULER * Z.inv_cdf(1 - 1 / (n * math.e)))


def sharpe_deflactado(m: Metricas, varianza_sr: float, n: int = N_INTENTOS) -> float:
    sr0 = sharpe_umbral(varianza_sr, n)
    sr = m.sharpe_mensual
    denom = math.sqrt(max(1 - m.asimetria * sr + (m.curtosis - 1) / 4 * sr**2, 1e-12))
    return Z.cdf((sr - sr0) * math.sqrt(m.meses - 1) / denom)


def varianza_liston(sharpes_mensuales: list[float], meses: int) -> float:
    return max(float(np.var(sharpes_mensuales, ddof=1)), 1.0 / meses)


def condicion_total(m: Metricas, ref: Metricas) -> bool:
    return m.tae >= ref.tae or (m.tae >= ref.tae - TOLERANCIA_TAE and m.caida <= FRACCION_CAIDA * ref.caida)


def anuales(valor_sin: pd.Series) -> pd.Series:
    """Rendimiento de cada anyo natural completo (antes de impuestos)."""
    fin = valor_sin.resample("YE").last()
    r = fin.pct_change()
    r.iloc[0] = fin.iloc[0] / valor_sin.iloc[0] - 1
    completos = [y for y in r.index.year if pd.Timestamp(f"{y}-12-31") <= valor_sin.index[-1] + pd.Timedelta(days=3)
                 and valor_sin.index[0] <= pd.Timestamp(f"{y}-01-05")]
    r.index = r.index.year
    return r.loc[completos]


def tipos_de_mercado(ref_anual: pd.Series, inflacion_anual: pd.Series) -> dict[str, list[int]]:
    """{tipo: [anyos]} con la regla P3 (un tipo con < 3 anyos se junta con el de su misma direccion de bolsa)."""
    tipos = {}
    for y, r in ref_anual.items():
        bolsa = "bajada" if r < 0 else "subida"
        infl = "inflacion alta" if inflacion_anual.get(y, np.nan) > INFLACION_ALTA else "inflacion baja"
        tipos.setdefault(f"{bolsa}, {infl}", []).append(int(y))
    final = {}
    for bolsa in ("bajada", "subida"):
        par = {k: v for k, v in tipos.items() if k.startswith(bolsa)}
        if any(len(v) < MIN_ANYOS_TIPO for v in par.values()):
            final[f"{bolsa} (juntos)"] = sorted(sum(par.values(), []))
        else:
            final.update(par)
    return final


def condicion_tipos(estr_anual: pd.Series, ref_anual: pd.Series, tipos: dict[str, list[int]]) -> dict[str, tuple]:
    """{tipo: (anyos, media de la diferencia, pasa)}."""
    out = {}
    for t, anyos in tipos.items():
        dif = float((estr_anual.loc[anyos] - ref_anual.loc[anyos]).mean())
        pasa = dif > 0 if t.startswith("bajada") else dif >= DETRAS_SUBIDA
        out[t] = (len(anyos), dif, pasa)
    return out


def inflacion_anual(cpi: pd.Series) -> pd.Series:
    """Diciembre sobre diciembre."""
    dic = cpi[cpi.index.month == 12]
    r = dic / dic.shift(1) - 1
    r.index = r.index.year
    return r.dropna()


def pbo_dos(r_base: pd.Series, r_modelo: pd.Series, grupos: int = 8) -> float:
    """Probabilidad de sobreajuste entre {base, base + modelo} (validacion combinatoria simetrica, 8 grupos)."""
    from itertools import combinations

    df = pd.concat([r_base, r_modelo], axis=1).dropna().to_numpy()
    trozos = np.array_split(np.arange(len(df)), grupos)

    def sr(x):
        sd = x.std(ddof=1)
        return x.mean() / sd if sd > 0 else 0.0

    peores = 0
    combos = list(combinations(range(grupos), grupos // 2))
    for c in combos:
        dentro = np.concatenate([trozos[g] for g in c])
        fuera = np.concatenate([trozos[g] for g in range(grupos) if g not in c])
        elegido = int(np.argmax([sr(df[dentro, j]) for j in range(2)]))
        fuera_sr = [sr(df[fuera, j]) for j in range(2)]
        peores += fuera_sr[elegido] < fuera_sr[1 - elegido]
    return peores / len(combos)
