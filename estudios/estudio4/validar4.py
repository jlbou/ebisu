"""Validacion del estudio 4 ANTES de medir (docs/plan-estudio-4.md 10.3). Todo con datos INVENTADOS, calculados a mano.

Sale "OK" o "FALLA"; si falla alguna, no se mide nada.

Uso: .venv/Scripts/python.exe estudios/estudio4/validar4.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import juez4 as J  # noqa: E402
import modelo4 as M  # noqa: E402
from montar import devengo, precio_par, rendimiento_bono  # noqa: E402
from simulador4 import (  # noqa: E402
    CAPITAL, Variante, cuartos_fiscales, cuota, factor_volatilidad, pesos_objetivo, referencia, simular)

FALLOS: list[str] = []
T = 0.19  # con importes pequenyos (por debajo de 6.000 €) solo cuenta el primer tramo


def comprobar(nombre: str, obtenido, esperado, tol: float = 1e-10) -> None:
    if isinstance(esperado, bool):
        ok = bool(obtenido) == esperado
    else:
        ok = abs(float(obtenido) - float(esperado)) <= tol
    print(f"{'OK   ' if ok else 'FALLA'} {nombre}: obtenido {obtenido}, esperado {esperado}")
    if not ok:
        FALLOS.append(nombre)


def piezas_sinteticas(semilla: int = 7, dias: int = 900) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    fechas = pd.bdate_range("2001-01-01", periods=dias)
    datos = {a: 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, dias))) for a in ("bolsa", "bonos", "oro")}
    datos["monetario"] = 100 * np.cumprod(np.full(dias, 1.0001))
    return pd.DataFrame(datos, index=fechas)


def simulador() -> None:
    pz = piezas_sinteticas()
    ini, fin = str(pz.index[0].date()), str(pz.index[-1].date())
    # 1. Todo en bolsa desde el primer dia y sin costes = comprar y mantener (fondo sin gastos).
    for fondos in (True, False):
        v = Variante("fijo", fondos=fondos, piezas=("bolsa",), coste_lado=0.0, calendario={ini: {"bolsa": 1.0}})
        r, ref = simular(pz, v, ini, fin), referencia(pz, ini, fin, gasto=0.0)
        comprobar(f"1. comprar y mantener ({'fondos' if fondos else 'ETF'})", r.bolsillo, ref.bolsillo)
    # 2. Impuestos por anyos con arrastre (importes pequenyos: 19 %).
    f = pd.bdate_range("2001-01-01", "2003-12-31")
    precio = pd.Series(100.0, index=f)
    precio[f >= "2001-06-01"] = 150.0
    precio[f >= "2002-03-01"] = 120.0
    precio[f >= "2002-09-02"] = 90.0
    precio[f >= "2003-06-02"] = 110.0
    pz3 = pd.DataFrame({"bolsa": precio, "bonos": 100.0, "oro": 100.0, "monetario": 100.0}, index=f)
    cal = {"2001-01-01": {"bolsa": 1.0}, "2001-10-01": {"bolsa": 0.0}, "2002-03-01": {"bolsa": 1.0},
           "2002-09-02": {"bolsa": 0.0}, "2003-03-03": {"bolsa": 1.0}}
    r = simular(pz3, Variante("imp", piezas=("bolsa",), coste_lado=0.0, calendario=cal), "2001-01-01", "2003-12-31")
    imp01 = T * 0.5
    v02 = 1.5 - imp01
    p02 = v02 * (90 / 120 - 1)
    g03 = (v02 + p02) * (110 / 90 - 1)
    imp03 = T * max(g03 + p02, 0)
    comprobar("2. impuestos por anyos con arrastre", r.impuestos, imp01 + imp03)
    sin = simular(pz3, Variante("imp", piezas=("bolsa",), coste_lado=0.0, calendario=cal, impuestos=False),
                  "2001-01-01", "2003-12-31")
    comprobar("2. sin impuestos: valor final = 1,5 x 90/120 x 110/90", sin.bolsillo, 1.5 * 110 / 120)
    # 3. Regla de los dos meses (como el estudio 1): recompra a las 3 semanas aplaza la perdida.
    precio = pd.Series(100.0, index=f)
    precio[f >= "2001-03-01"] = 120.0
    precio[f >= "2001-05-01"] = 80.0
    precio[f >= "2002-01-02"] = 100.0
    pz4 = pd.DataFrame({"bolsa": precio, "bonos": 100.0, "oro": 100.0, "monetario": 100.0}, index=f)
    base = {"2001-01-01": {"bolsa": 0.5}, "2001-03-01": {"bolsa": 0.0}, "2001-04-02": {"bolsa": 0.5},
            "2001-06-01": {"bolsa": 0.0}}
    con = simular(pz4, Variante("c", piezas=("bolsa",), coste_lado=0.0, calendario={**base, "2001-06-22": {"bolsa": 0.5}}),
                  "2001-01-01", "2003-12-31")
    sin = simular(pz4, Variante("s", piezas=("bolsa",), coste_lado=0.0, calendario={**base, "2001-09-03": {"bolsa": 0.5}}),
                  "2001-01-01", "2003-12-31")
    d = pd.Timestamp("2001-12-31")
    comprobar("3. dos meses: la recompra en 3 semanas paga la ganancia de marzo", float(sin.valor[d] - con.valor[d]),
              T * 0.1)
    # 4. Tramos: ganancia grande (de 1 a 101 por euro; 25.000 € de base) en la referencia.
    fr = pd.bdate_range("2001-01-01", periods=3)
    pzr = pd.DataFrame({"bolsa": [1.0, 50.0, 101.0], "monetario": 1.0}, index=fr)
    r = referencia(pzr, str(fr[0].date()), str(fr[-1].date()), gasto=0.0)
    comprobar("4. referencia con tramos (25.000 € de ganancia)", r.impuestos * CAPITAL, 6000 * 0.19 + 19000 * 0.21, 1e-6)


def impuestos() -> None:
    comprobar("5. cuota de 6.000 €", cuota(6000), 1140)
    comprobar("5. cuota de 60.000 € (ejemplo de la fuente)", cuota(60000), 12680)
    comprobar("5. cuota de 350.000 €", cuota(350000), 1140 + 9240 + 34500 + 27000 + 15000)
    comprobar("5. cuota de 0", cuota(0), 0)


def bonos() -> None:
    y = np.array([0.05])
    comprobar("6. bono a la par vale 1", precio_par(y, y)[0], 1.0, 1e-12)
    dur = (1 / 0.05) * (1 - (1 + 0.025) ** -14)  # duracion modificada de un bono a la par (semestral)
    cambio = precio_par(np.array([0.0501]), y)[0] - 1
    # Diferencia permitida: la convexidad (0,5 x C x 0,0001^2, con C ~40 para 7 anyos: ~2e-7).
    comprobar("6. +1 pb cambia el precio en -duracion x 0,0001", cambio, -dur * 0.0001, 5e-7)
    f = pd.DatetimeIndex(["2001-01-01", "2001-01-02", "2001-01-03"])
    r = rendimiento_bono(pd.Series([5.0, 5.0, 5.0], index=f), f)
    comprobar("6. sin cambio de rentabilidad, solo devengo (1 dia)", r.iloc[1], 0.05 / 365, 1e-12)
    fd = pd.DatetimeIndex(["2001-01-01", "2001-01-11"])
    comprobar("7. devengo de 10 dias al 3,6 %", devengo(pd.Series([3.6], index=fd[:1]), fd).iloc[1], 1.001, 1e-12)


def capas() -> None:
    n = 900
    r = np.tile([0.01, -0.01], n // 2)
    r[-63:] = np.tile([0.02, -0.02], 32)[:63]
    s = pd.Series(np.cumprod(1 + r), index=pd.bdate_range("2001-01-01", periods=n))
    fac = factor_volatilidad(s)
    comprobar("8. capa 2: volatilidad doble -> factor ~0,5", fac.iloc[-1], 0.5, 0.01)
    comprobar("8. capa 2: con menos de 2 anyos de historia, factor 1", fac.iloc[400], 1.0)
    comprobar("8. capa 2: nunca por encima de 1", float(fac.max()), 1.0)
    cuenta = pd.Series([4, 3, 3, 2, 1, 0, 2], dtype=float)
    comprobar("9. capa 3: 4,3,3,2,1,0,2 -> 4,4,4,2,2,0,2", float((cuartos_fiscales(cuenta).to_numpy()
                                                                  == [4, 4, 4, 2, 2, 0, 2]).all()), 1.0)
    pz = piezas_sinteticas(dias=400)
    v = Variante("x")
    base = pesos_objetivo(pz, v)
    mult = pd.Series(0.5, index=base.index)
    con = pesos_objetivo(pz, Variante("y", multiplicador=mult))
    comprobar("10. capa 6: la bolsa a la mitad", float((con["bolsa"] - base["bolsa"] / 2).abs().max()), 0.0)
    comprobar("10. capa 6: bonos y oro sin tocar", float((con[["bonos", "oro"]] - base[["bonos", "oro"]]).abs().max().max()),
              0.0)


def juez() -> None:
    ref = pd.Series({1971: -0.1, 1972: 0.2, 1973: -0.2, 1974: 0.1, 1975: 0.15, 1976: -0.05, 1977: 0.3, 1978: 0.05})
    infl = pd.Series({1971: 0.05, 1972: 0.05, 1973: 0.06, 1974: 0.02, 1975: 0.02, 1976: 0.02, 1977: 0.07, 1978: 0.01})
    tipos = J.tipos_de_mercado(ref, infl)
    comprobar("11. tipos: bajadas (2 alta + 1 baja) se juntan", tipos.get("bajada (juntos)") == [1971, 1973, 1976], True)
    comprobar("11. tipos: subidas (2 alta + 3 baja) se juntan", tipos.get("subida (juntos)") == [1972, 1974, 1975, 1977, 1978],
              True)
    est = ref + pd.Series({1971: 0.12, 1972: -0.06, 1973: 0.25, 1974: -0.04, 1975: -0.05, 1976: 0.0, 1977: -0.1,
                           1978: -0.02})
    c = J.condicion_tipos(est, ref, tipos)
    comprobar("11. tipos: bajadas, media de +12,3 % -> pasa", c["bajada (juntos)"][2], True)
    comprobar("11. tipos: subidas, media de -5,4 % -> no pasa", c["subida (juntos)"][2], False)
    comprobar("11. tipos: media de las subidas", c["subida (juntos)"][1], -0.054, 1e-12)
    cpi = pd.Series([100.0, 103.0, 110.0], index=pd.to_datetime(["1970-12-31", "1971-12-31", "1972-12-31"]))
    comprobar("12. inflacion diciembre sobre diciembre", J.inflacion_anual(cpi)[1972], 110 / 103 - 1, 1e-12)
    m = J.Metricas(0, 0, 0, sharpe_mensual=0.15, asimetria=0.0, curtosis=3.0, meses=600)
    a_mano = J.Z.cdf(0.15 * math.sqrt(599) / math.sqrt(1 + 2 / 4 * 0.15**2))
    comprobar("13. deflactado con N = 1 = Sharpe probabilistico", J.sharpe_deflactado(m, 0.0, 1), a_mano)
    comprobar("13. varianza del liston: al menos la de pura suerte", J.varianza_liston([0.1, 0.1, 0.1], 600), 1 / 600)
    ref_m = J.Metricas(0.08, 0.45, 0, 0, 0, 3, 0)
    comprobar("14. total: 7,1 % y cae 30 % (<= 2/3) pasa", J.condicion_total(J.Metricas(0.071, 0.30, 0, 0, 0, 3, 0), ref_m),
              True)
    comprobar("14. total: 6,9 % (mas de 1 punto por debajo) no pasa",
              J.condicion_total(J.Metricas(0.069, 0.10, 0, 0, 0, 3, 0), ref_m), False)
    rng = np.random.default_rng(1)
    rb = pd.Series(rng.normal(0.005, 0.03, 480))
    comprobar("15. PBO de dos estrategias iguales = 0", J.pbo_dos(rb, rb.copy()), 0.0)
    comprobar("15. PBO si el modelo es siempre mejor = 0", J.pbo_dos(rb, rb + 0.01), 0.0)


def modelo() -> None:
    rng = np.random.default_rng(5)
    meses = pd.date_range("1930-01-31", "1975-12-31", freq="ME")
    rend = pd.Series(rng.normal(0.008, 0.05, len(meses)), index=meses)
    cortes = [meses[100], meses[300], meses[-1]]
    comprobar("16. las variables no miran el futuro", M.sin_futuro(M.variables_de, rend, cortes), True)

    def con_trampa(x: pd.Series) -> pd.DataFrame:
        v = M.variables_de(x)
        v["trampa"] = x.shift(-1)  # el rendimiento del mes siguiente
        return v

    comprobar("16. una variable que mira el futuro se detecta", M.sin_futuro(con_trampa, rend, cortes), False)
    sec = pd.DataFrame(rng.normal(0.008, 0.05, (len(meses), 5)), index=meses, columns=list("ABCDE"))
    rf = pd.Series(0.003, index=meses)
    infl = pd.Series(rng.normal(0.03, 0.01, len(meses)), index=meses)
    muestras = M.panel(sec, rf, infl)
    comprobar("17. el panel solo tiene meses con senyal 'dentro'", float((muestras["encima"] == 1).all()), 1.0)
    comprobar("17. la etiqueta acaba despues de la decision", float((muestras["fin_etiqueta"] > muestras.index).all()), 1.0)
    dias = pd.bdate_range("1960-01-01", "1975-12-31")
    bolsa = pd.Series(np.exp(np.cumsum(rng.normal(0.0003, 0.01, len(dias)))), index=dias)
    senyales = pd.DatetimeIndex(bolsa.groupby(bolsa.index.to_period("M")).apply(lambda s: s.index.max()).to_numpy())
    f, imp = M.multiplicador(bolsa, senyales, range(1970, 1976), sec, rf, infl)
    comprobar("18. el multiplicador solo vale 1 o 0,5", float(f.isin([0.5, 1.0]).all()), 1.0)
    comprobar("18. sin modelo antes de 1970 (factor 1)", float((f[f.index.year < 1970] == 1.0).all()), 1.0)
    comprobar("18. importancia entre 0 y 1", float(0 < imp <= 1), 1.0)
    ent = muestras[muestras["fin_etiqueta"] <= pd.Timestamp("1968-12-31")]
    comprobar("19. el modelo de 1970 se entrena solo hasta 1968", float(ent["fin_etiqueta"].max() <= pd.Timestamp("1968-12-31")),
              1.0)


def main() -> None:
    simulador()
    impuestos()
    bonos()
    capas()
    juez()
    modelo()
    print()
    print("VALIDACION DEL ESTUDIO 4:", "TODO OK" if not FALLOS else f"FALLAN {len(FALLOS)}: {', '.join(FALLOS)}")
    sys.exit(1 if FALLOS else 0)


if __name__ == "__main__":
    main()
