"""Juez del estudio 1: aplica la seccion 6 de docs/diseno-estudio-1.md y escribe el veredicto. Nadie lo interpreta.

Metricas, sobre lo que quedaria en el bolsillo tras venderlo todo y pagar lo pendiente:
- TAE: bolsillo ^ (1 / anyos) - 1.
- Caida maxima: la peor bajada desde un maximo del valor diario (impuestos ya pagados restados).
- Sharpe anual: media / desviacion de (rendimiento diario - rendimiento diario del monetario) x raiz de 252.
- Sharpe deflactado (Bailey y Lopez de Prado, 2014), con N = 5 y la varianza de los Sharpe de las N variantes.

Condiciones (exploracion): 1) TAE >= la de la referencia, o TAE >= la de la referencia - 1 punto y caida <= 2/3 de la
de la referencia; 2) TAE > 0; 3) Sharpe deflactado >= 0,95. H2, ademas: IC del 90 % del rendimiento medio por operacion
por encima de 0 (juntando los 7 pares) y media positiva en >= 5 de 7 pares. Reserva: 1 y 2.

Uso:
  .venv/Scripts/python.exe estudios/estudio1/juez.py --validar      (datos inventados; no mide nada)
  La medicion (--medir exploracion) se anyade cuando esten los datos de H2: el liston cuenta las 5 variantes juntas.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np
import pandas as pd

N_VARIANTES = 5
EULER = 0.5772156649015329
LISTON_DSR = 0.95
TOLERANCIA_TAE = 0.01
FRACCION_CAIDA = 2 / 3
Z = NormalDist()


@dataclass
class Metricas:
    tae: float
    caida: float
    sharpe: float  # anual
    sharpe_diario: float
    asimetria: float
    curtosis: float  # no en exceso (normal = 3)
    dias: int


def metricas(valor: pd.Series, bolsillo: float, monetario: pd.Series) -> Metricas:
    anyos = (valor.index[-1] - valor.index[0]).total_seconds() / 86400 / 365.25
    tae = bolsillo ** (1 / anyos) - 1
    caida = float((1 - valor / valor.cummax()).max())
    exceso = (valor.pct_change() - monetario.reindex(valor.index).pct_change()).dropna()
    sd = float(exceso.std(ddof=1))
    sr_d = float(exceso.mean()) / sd if sd > 0 else 0.0
    return Metricas(tae, caida, sr_d * math.sqrt(252), sr_d, float(exceso.skew()), float(exceso.kurt()) + 3.0,
                    len(exceso))


def sharpe_umbral(varianza_sr: float, n: int) -> float:
    """Sharpe maximo esperado por pura suerte entre n pruebas (por periodo)."""
    if n <= 1:
        return 0.0
    return math.sqrt(varianza_sr) * ((1 - EULER) * Z.inv_cdf(1 - 1 / n) + EULER * Z.inv_cdf(1 - 1 / (n * math.e)))


def sharpe_deflactado(m: Metricas, varianza_sr: float, n: int = N_VARIANTES) -> float:
    sr0 = sharpe_umbral(varianza_sr, n)
    sr = m.sharpe_diario
    denom = math.sqrt(max(1 - m.asimetria * sr + (m.curtosis - 1) / 4 * sr**2, 1e-12))
    return Z.cdf((sr - sr0) * math.sqrt(m.dias - 1) / denom)


def pasa(m: Metricas, ref: Metricas, dsr: float | None) -> dict[str, bool]:
    c1 = m.tae >= ref.tae or (m.tae >= ref.tae - TOLERANCIA_TAE and m.caida <= FRACCION_CAIDA * ref.caida)
    r = {"1. gana o casi iguala con menos caida": c1, "2. no pierde": m.tae > 0}
    if dsr is not None:
        r["3. no es suerte (deflactado >= 0,95)"] = dsr >= LISTON_DSR
    return r


def pasa_h2(por_operacion: dict[str, np.ndarray]) -> dict[str, bool]:
    todas = np.concatenate(list(por_operacion.values()))
    media, sd = float(todas.mean()), float(todas.std(ddof=1))
    bajo = media - 1.6448536269514722 * sd / math.sqrt(len(todas))
    positivos = sum(float(v.mean()) > 0 for v in por_operacion.values())
    return {"H2. IC 90 % por operacion > 0": bajo > 0, "H2. positiva en >= 5 de 7 pares": positivos >= 5}


# ---------------------------------------------------------------------------------------------------------------------
# Validacion con datos inventados
# ---------------------------------------------------------------------------------------------------------------------

FALLOS: list[str] = []


def comprobar(nombre: str, obtenido, esperado, tol: float = 1e-9) -> None:
    ok = (obtenido == esperado) if isinstance(esperado, bool) else abs(obtenido - esperado) <= tol
    print(f"{'OK   ' if ok else 'FALLA'} {nombre}: obtenido {obtenido}, esperado {esperado}")
    if not ok:
        FALLOS.append(nombre)


def validar() -> None:
    # TAE: de 1 a 2 en dos anyos exactos (730,5 dias) -> raiz de 2 - 1.
    f = pd.date_range("2001-01-01", periods=2, freq="730D12h")
    v = pd.Series([1.0, 2.0], index=f)
    comprobar("TAE de 1 a 2 en dos anyos", metricas(v, 2.0, v).tae, math.sqrt(2) - 1)

    # Caida maxima: 1 -> 2 -> 1 -> 3: la peor es del 50 %.
    f = pd.bdate_range("2001-01-01", periods=4)
    v = pd.Series([1.0, 2.0, 1.0, 3.0], index=f)
    comprobar("caida maxima 1-2-1-3", metricas(v, 3.0, pd.Series(1.0, index=f)).caida, 0.5)

    # Sharpe: rendimientos alternos +2 % y 0 % con monetario plano -> media 1 %, sd conocida.
    rend = np.tile([0.02, 0.0], 50)
    f = pd.bdate_range("2001-01-01", periods=101)
    v = pd.Series(np.concatenate([[1.0], np.cumprod(1 + rend)]), index=f)
    sd = float(pd.Series(rend).std(ddof=1))
    comprobar("Sharpe anual con datos conocidos", metricas(v, float(v.iloc[-1]), pd.Series(1.0, index=f)).sharpe,
              0.01 / sd * math.sqrt(252))

    # Deflactado con una sola prueba = Sharpe probabilistico contra 0 (formula a mano, normal: asimetria 0, curtosis 3).
    m = Metricas(0, 0, 0, sharpe_diario=0.05, asimetria=0.0, curtosis=3.0, dias=1000)
    a_mano = Z.cdf(0.05 * math.sqrt(999) / math.sqrt(1 + 2 / 4 * 0.05**2))
    comprobar("deflactado con N = 1 = Sharpe probabilistico", sharpe_deflactado(m, 0.0, 1), a_mano)

    # Umbral de suerte: formula del articulo para N = 5 y varianza 0,0004 (desviacion 0,02).
    a_mano = 0.02 * ((1 - EULER) * Z.inv_cdf(0.8) + EULER * Z.inv_cdf(1 - 1 / (5 * math.e)))
    comprobar("Sharpe por suerte con N = 5", sharpe_umbral(0.0004, 5), a_mano)

    # Mas pruebas -> deflactado mas bajo.
    comprobar("mas variantes, liston mas alto", sharpe_deflactado(m, 0.0004, 10) < sharpe_deflactado(m, 0.0004, 5), True)

    # Condiciones con numeros inventados (referencia: TAE 6 %, caida 50 %).
    ref = Metricas(0.06, 0.50, 0, 0, 0, 3, 0)
    casos = [
        ("gana a la referencia", Metricas(0.065, 0.55, 0, 0, 0, 3, 0), True),
        ("5,2 % y cae 30 % (<= 2/3)", Metricas(0.052, 0.30, 0, 0, 0, 3, 0), True),
        ("5,2 % y cae 40 % (> 2/3)", Metricas(0.052, 0.40, 0, 0, 0, 3, 0), False),
        ("4,9 % y cae 10 % (mas de 1 punto por debajo)", Metricas(0.049, 0.10, 0, 0, 0, 3, 0), False),
    ]
    for nombre, mm, esperado in casos:
        comprobar(f"condicion 1: {nombre}", pasa(mm, ref, None)["1. gana o casi iguala con menos caida"], esperado)
    comprobar("condicion 2: pierde", pasa(Metricas(-0.001, 0.1, 0, 0, 0, 3, 0), ref, None)["2. no pierde"], False)
    comprobar("condicion 3: deflactado 0,949", pasa(ref, ref, 0.949)["3. no es suerte (deflactado >= 0,95)"], False)

    # H2: siete pares con media positiva clara -> pasa; con solo 4 pares positivos -> no.
    rng = np.random.default_rng(3)
    buenos = {f"P{i}": rng.normal(0.001, 0.005, 2000) for i in range(7)}
    comprobar("H2: 7 pares buenos pasan las dos", all(pasa_h2(buenos).values()), True)
    mixtos = {f"P{i}": rng.normal(0.001 if i < 4 else -0.0005, 0.005, 2000) for i in range(7)}
    comprobar("H2: solo 4 de 7 positivos no pasa", pasa_h2(mixtos)["H2. positiva en >= 5 de 7 pares"], False)

    print()
    print("VALIDACION DEL JUEZ:", "TODO OK" if not FALLOS else f"FALLAN {len(FALLOS)}: {', '.join(FALLOS)}")
    sys.exit(1 if FALLOS else 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validar", action="store_true", help="pruebas con datos inventados (no mide nada)")
    args = ap.parse_args()
    if args.validar:
        validar()
    else:
        sys.exit("La medicion aun no esta habilitada: faltan los datos de H2 (las 5 variantes se juzgan juntas).")


if __name__ == "__main__":
    main()
