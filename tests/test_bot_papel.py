"""Pruebas del papel y del juez con precios INVENTADOS (sin red). Incluye la prueba de oro con el simulador del estudio."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ebisu import juez as J
from ebisu import papel as P
from ebisu.precios import Aviso

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "estudios" / "estudio4"))
import simulador4 as S  # noqa: E402


@pytest.fixture(scope="module")
def cierres() -> pd.DataFrame:
    rng = np.random.default_rng(21)
    f = pd.bdate_range("2019-01-01", "2026-10-15")
    c = pd.DataFrame({a: 50 * np.exp(np.cumsum(rng.normal(0.0002, 0.012, len(f)))) for a in ("bolsa", "bonos", "oro")},
                     index=f)
    c["monetario"] = 100 * np.cumprod(np.full(len(f), 1.0001))
    c.loc[c.sample(frac=0.02, random_state=1).index, "oro"] = np.nan  # festivos de una sola bolsa
    return c


SENYAL = pd.Timestamp("2024-03-29")  # ultimo dia habil de marzo de 2024
HASTA = pd.Timestamp("2026-10-15")


@pytest.fixture(scope="module")
def papel(cierres) -> P.Papel:
    return P.calcular(cierres, SENYAL, HASTA)


def test_prueba_de_oro_igual_que_el_simulador_del_estudio(cierres, papel):
    piezas = P.piezas_de(cierres).loc[:HASTA]
    inicio = P.dia_de_ejecucion(piezas, SENYAL)
    r = S.simular(piezas, S.Variante("H1-M"), str(inicio.date()), str(HASTA.date()))
    assert papel.valor.equals(r.valor)
    assert papel.si_vende_hoy_eur == pytest.approx(P.CAPITAL_EUR * r.bolsillo, abs=1e-12)


def test_empieza_el_dia_de_ejecucion_en_el_monetario(cierres, papel):
    assert papel.valor.index[0] == pd.Timestamp("2024-04-01")
    assert papel.operaciones[0].fecha == pd.Timestamp("2024-04-01")


def test_las_operaciones_cuadran_con_la_estrategia(papel):
    assert len(papel.operaciones) == papel.operaciones_estrategia > 0
    assert all(o.tipo in ("compra", "venta") for o in papel.operaciones)
    assert sum(papel.pesos.values()) <= 1 + 1e-12 and all(w <= 1 / 3 + 1e-12 for w in papel.pesos.values())


def test_referencia_es_la_bolsa_mantenida(cierres, papel):
    piezas = P.piezas_de(cierres)
    b = piezas["bolsa"].loc["2024-04-01":HASTA]
    assert papel.referencia_eur == pytest.approx(P.CAPITAL_EUR * b.iloc[-1] / b.iloc[0])


def test_solo_las_nuevas(papel):
    ayer = papel.operaciones[-1].fecha - pd.Timedelta(days=1)
    nuevas = P.nuevas(papel, ayer)
    assert nuevas and all(o.fecha > ayer for o in nuevas)
    assert P.nuevas(papel, None) == papel.operaciones


def test_rehacerlo_da_lo_mismo(cierres, papel):
    otra = P.calcular(cierres, SENYAL, HASTA)
    assert otra.valor.equals(papel.valor) and otra.operaciones == papel.operaciones


def test_sin_dia_de_ejecucion_todavia(cierres):
    with pytest.raises(ValueError):
        P.calcular(cierres, HASTA, HASTA)


def test_juez_sin_incidencias(papel):
    senyales = [pd.Timestamp("2026-09-30")]
    assert J.juzgar(papel, "h", "h", senyales, {pd.Timestamp("2026-09-30")}, []) == []


def test_juez_cada_incidencia(papel):
    from dataclasses import replace

    malo = replace(papel, caida=0.20, operaciones_estrategia=papel.operaciones_estrategia + 1)
    inc = J.juzgar(malo, "a", "b", [pd.Timestamp("2026-09-30")], set(),
                   [Aviso("salto", "oro", "x"), Aviso("ajuste", "bolsa", "y")])
    tipos = {i.tipo for i in inc}
    assert tipos == {"huella", "coherencia", "caida", "senyal_sin_vuelta", "precios"}
    graves = {(i.tipo, i.grave) for i in inc if i.tipo == "precios"}
    assert graves == {("precios", True), ("precios", False)}


def test_no_pasa_del_ultimo_dia_con_las_4_piezas(cierres):
    c = cierres.copy()
    c.loc[pd.Timestamp("2026-10-14"):, "oro"] = np.nan  # el oro aun no ha llegado
    papel = P.calcular(c, SENYAL, HASTA)
    assert papel.hasta == pd.Timestamp("2026-10-13")


def test_senyales_reales_y_puntos(cierres, papel):
    piezas = P.piezas_de(cierres)
    s = P.senyales_reales(piezas, pd.Timestamp("2026-10-15"))
    assert s[-1] == pd.Timestamp("2026-09-30")
    assert P.senyales_reales(piezas, pd.Timestamp("2026-09-30"))[-1] == pd.Timestamp("2026-09-30")
    assert papel.ultima_senyal == pd.Timestamp("2026-09-30")
    assert set(papel.puntos) == {"bolsa", "bonos", "oro"} and all(0 <= v <= 4 for v in papel.puntos.values())
