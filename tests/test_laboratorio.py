"""Pruebas de la idea 1 del laboratorio con precios INVENTADOS (sin red)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ebisu.laboratorio import costes as C
from ebisu.laboratorio import juez_idea as J
from ebisu.laboratorio import regla_rango as R


def barras(inicio: str, filas: list[tuple[float, float, float]]) -> pd.DataFrame:
    """Barras de 5 minutos desde `inicio` (UTC); cada fila es (high, low, close)."""
    indice = pd.date_range(inicio, periods=len(filas), freq="5min", tz="UTC")
    return pd.DataFrame(filas, index=indice, columns=["high", "low", "close"])


# --- costes ---------------------------------------------------------------------------------------------------

def test_spread_en_precio_por_par_y_multiplo():
    assert C.spread_en_precio("EURUSD", 1.2) == pytest.approx(0.00012)
    assert C.spread_en_precio("USDJPY", 1.2) == pytest.approx(0.012)  # con el ien, el pip es 0,01
    assert C.spread_en_precio("EURUSD", 1.2, multiplo=2) == pytest.approx(0.00024)


def test_spread_desconocido_o_negativo_falla():
    with pytest.raises(ValueError):
        C.spread_en_precio("GBPUSD")
    with pytest.raises(ValueError):
        C.spread_en_precio("EURUSD", pips=-1)


# --- sesiones y niveles ---------------------------------------------------------------------------------------

def test_la_sesion_cambia_a_las_17_de_nueva_york_en_invierno_y_en_verano():
    inv = pd.DatetimeIndex(["2026-11-16 21:55", "2026-11-16 22:00"], tz="UTC")  # 16:55 y 17:00 en Nueva York (EST)
    ver = pd.DatetimeIndex(["2026-07-15 20:55", "2026-07-15 21:00"], tz="UTC")  # 16:55 y 17:00 en Nueva York (EDT)
    assert list(R.etiquetar_sesiones(inv)) == [pd.Timestamp("2026-11-16"), pd.Timestamp("2026-11-17")]
    assert list(R.etiquetar_sesiones(ver)) == [pd.Timestamp("2026-07-15"), pd.Timestamp("2026-07-16")]


def test_el_domingo_por_la_tarde_pertenece_a_la_sesion_del_lunes():
    domingo = pd.DatetimeIndex(["2026-11-15 22:00"], tz="UTC")  # domingo 17:00 en Nueva York
    assert R.etiquetar_sesiones(domingo)[0] == pd.Timestamp("2026-11-16")


def test_el_indice_sin_zona_horaria_falla():
    with pytest.raises(ValueError):
        R.etiquetar_sesiones(pd.DatetimeIndex(["2026-11-16 22:00"]))


def test_niveles_con_x_cero_y_con_veinte_por_ciento():
    assert R.niveles(1.1100, 1.1000, 0.0) == pytest.approx((1.1000, 1.1100))
    assert R.niveles(1.1100, 1.1000, 0.2) == pytest.approx((1.1020, 1.1080))


def test_niveles_rechaza_x_o_rangos_invalidos():
    for x in (-0.1, 0.5, 0.7):
        with pytest.raises(ValueError):
            R.niveles(1.11, 1.10, x)
    with pytest.raises(ValueError):
        R.niveles(1.10, 1.10, 0.2)


# --- una sesion -----------------------------------------------------------------------------------------------

SPREAD = 0.0002  # 2 pips: la mitad es 0,0001


def test_tocar_el_nivel_no_basta_hay_que_cruzar_la_mitad_del_spread():
    compra, objetivo = 1.1020, 1.1080
    toca = barras("2026-11-17 22:00", [(1.1050, 1.10195, 1.1040), (1.1050, 1.1030, 1.1040)])  # 1.10195 > 1.1019
    cruza = barras("2026-11-17 22:00", [(1.1050, 1.1019, 1.1040), (1.1050, 1.1030, 1.1040)])
    assert R.simular_sesion("EURUSD", pd.Timestamp("2026-11-18"), toca, compra, objetivo, SPREAD) is None
    assert R.simular_sesion("EURUSD", pd.Timestamp("2026-11-18"), cruza, compra, objetivo, SPREAD) is not None


def test_la_salida_en_el_objetivo_necesita_cruzar_la_mitad_del_spread():
    compra, objetivo = 1.1020, 1.1080
    # entra en la barra 1; el maximo de la barra 2 (1.1080) solo toca el objetivo: no sale ahi
    sin = barras("2026-11-17 22:00", [(1.1050, 1.1030, 1.1040), (1.1040, 1.1018, 1.1030), (1.1080, 1.1030, 1.1050)])
    op = R.simular_sesion("EURUSD", pd.Timestamp("2026-11-18"), sin, compra, objetivo, SPREAD)
    assert op.motivo == "cierre"
    con = barras("2026-11-17 22:00", [(1.1050, 1.1030, 1.1040), (1.1040, 1.1018, 1.1030), (1.1081, 1.1030, 1.1050)])
    op = R.simular_sesion("EURUSD", pd.Timestamp("2026-11-18"), con, compra, objetivo, SPREAD)
    assert op.motivo == "objetivo"
    assert op.precio_entrada == pytest.approx(1.1020) and op.precio_salida == pytest.approx(1.1080)
    assert op.neto == pytest.approx(0.0060) and op.bruto == pytest.approx(0.0062)


def test_dentro_de_la_barra_de_entrada_no_se_sale_aunque_toque_el_objetivo():
    compra, objetivo = 1.1020, 1.1080
    b = barras("2026-11-17 22:00", [(1.1090, 1.1018, 1.1050), (1.1060, 1.1040, 1.1050)])  # entra y "sale" en la 0
    op = R.simular_sesion("EURUSD", pd.Timestamp("2026-11-18"), b, compra, objetivo, SPREAD)
    assert op.motivo == "cierre" and op.salida == b.index[-1]
    assert op.precio_salida == pytest.approx(1.1050 - 0.0001)  # cierre medio menos la mitad del spread


def test_entrada_en_la_ultima_barra_se_cierra_en_ella():
    b = barras("2026-11-17 22:00", [(1.1050, 1.1030, 1.1040), (1.1040, 1.1018, 1.1030)])
    op = R.simular_sesion("EURUSD", pd.Timestamp("2026-11-18"), b, 1.1020, 1.1080, SPREAD)
    assert op.entrada == op.salida == b.index[-1]


def test_sin_compra_no_hay_operacion():
    b = barras("2026-11-17 22:00", [(1.1060, 1.1045, 1.1050), (1.1065, 1.1042, 1.1060)])
    assert R.simular_sesion("EURUSD", pd.Timestamp("2026-11-18"), b, 1.1020, 1.1080, SPREAD) is None


# --- varias sesiones ------------------------------------------------------------------------------------------

def _cuatro_sesiones() -> pd.DataFrame:
    s1 = barras("2026-11-16 22:00", [(1.1100, 1.1050, 1.1060), (1.1080, 1.1000, 1.1090), (1.1100, 1.1070, 1.1090)])
    s2 = barras("2026-11-17 22:00", [(1.1050, 1.1030, 1.1040), (1.1040, 1.1018, 1.1030), (1.1085, 1.1030, 1.1070)])
    s3 = barras("2026-11-18 22:00", [(1.1060, 1.1045, 1.1050), (1.1065, 1.1042, 1.1060)])
    s4 = barras("2026-11-19 22:00", [(1.1062, 1.1044, 1.1050), (1.1058, 1.1040, 1.1052), (1.1056, 1.1040, 1.1050)])
    return pd.concat([s1, s2, s3, s4])


def test_simular_varias_sesiones_el_dia_sin_compra_no_da_operacion():
    ops = R.simular("EURUSD", _cuatro_sesiones(), x=0.2, spread=SPREAD)
    assert [op.sesion for op in ops] == [pd.Timestamp("2026-11-18"), pd.Timestamp("2026-11-20")]
    assert [op.motivo for op in ops] == ["objetivo", "cierre"]
    assert ops[0].neto == pytest.approx(0.0060)
    assert ops[1].neto == pytest.approx(1.1050 - 0.0001 - ops[1].precio_entrada)


def test_la_primera_sesion_solo_da_el_rango_y_no_opera():
    ops = R.simular("EURUSD", _cuatro_sesiones(), x=0.2, spread=SPREAD)
    assert all(op.sesion > pd.Timestamp("2026-11-17") for op in ops)


def test_con_mas_spread_hay_menos_o_iguales_operaciones_y_cada_una_gana_menos():
    uno = R.simular("EURUSD", _cuatro_sesiones(), 0.2, SPREAD)
    tres = R.simular("EURUSD", _cuatro_sesiones(), 0.2, 3 * SPREAD)
    assert len(tres) <= len(uno)


def _op(par: str, entrada: str, salida: str) -> R.Operacion:
    t0, t1 = pd.Timestamp(entrada, tz="UTC"), pd.Timestamp(salida, tz="UTC")
    return R.Operacion(par, t0.normalize().tz_localize(None), t0, t1, 1.10, 1.11, 0.0001, "objetivo")


def test_una_sola_posicion_en_total():
    a = _op("EURUSD", "2026-11-18 10:00", "2026-11-18 12:00")
    b = _op("USDJPY", "2026-11-18 11:00", "2026-11-18 13:00")  # llega con la anterior abierta: no se ejecuta
    c = _op("USDJPY", "2026-11-18 12:00", "2026-11-18 14:00")  # entra justo cuando sale la anterior: si
    assert R.una_posicion([a], [b, c]) == [a, c]


# --- el juez --------------------------------------------------------------------------------------------------

def _ops(netas, spread: float = 0.0001, precio: float = 1.10) -> list[R.Operacion]:
    t = pd.Timestamp("2026-11-18 10:00", tz="UTC")
    return [R.Operacion("EURUSD", t.normalize().tz_localize(None), t + pd.Timedelta(days=i), t + pd.Timedelta(days=i, hours=1),
                        precio, precio + n, spread, "objetivo") for i, n in enumerate(netas)]


def _rng(n: int, media: float, desv: float) -> np.ndarray:
    return np.random.default_rng(3).normal(media, desv, n)


def test_pasa_con_ganancia_clara_margen_y_sin_caida():
    netas = _rng(250, 0.0010, 0.0002)
    v = J.juzgar(_ops(netas), _ops(netas - 0.0001, 0.0002), meses=4, n_pruebas=4, sesiones=300)
    assert v.estado == "pasa" and v.razones == ()
    assert v.limite_inferior > 0 and v.margen > J.MARGEN_MIN and v.caida < J.CAIDA_MAX
    assert v.dias_sin_compra == 50


def test_pendiente_si_faltan_operaciones_o_meses():
    netas = _rng(50, 0.0010, 0.0002)
    assert J.juzgar(_ops(netas), _ops(netas), meses=1, n_pruebas=4).estado == "pendiente"
    netas = _rng(250, 0.0010, 0.0002)
    assert J.juzgar(_ops(netas), _ops(netas), meses=2, n_pruebas=4).estado == "pendiente"


def test_parada_temprana_a_las_100_operaciones_si_el_limite_superior_es_negativo():
    netas = _rng(120, -0.0005, 0.0001)
    v = J.juzgar(_ops(netas), _ops(netas), meses=2, n_pruebas=4)
    assert v.estado == "descartada_temprano" and v.limite_superior < 0


def test_sin_100_operaciones_no_hay_parada_temprana():
    netas = _rng(80, -0.0005, 0.0001)
    assert J.juzgar(_ops(netas), _ops(netas), meses=2, n_pruebas=4).estado == "pendiente"


def test_no_pasa_si_el_margen_bruto_sobre_coste_es_bajo():
    netas = _rng(250, 0.00005, 0.00001)  # bruto 0,00015 sobre un coste de 0,0001: margen 1,5
    v = J.juzgar(_ops(netas), _ops(netas - 0.0001, 0.0002), meses=4, n_pruebas=4)
    assert v.estado == "no_pasa"
    assert any("margen" in r for r in v.razones) and any("2x" in r for r in v.razones)


def test_no_pasa_si_la_caida_supera_el_limite():
    netas = np.concatenate([[-0.088], _rng(250, 0.0010, 0.0002)])  # una perdida del 8 %: a 4x son 80 de 250 (32 %)
    v = J.juzgar(_ops(netas), _ops(netas - 0.0001, 0.0002), meses=4, n_pruebas=4)
    assert v.estado == "no_pasa" and any("caida" in r for r in v.razones)


def test_mas_pruebas_endurecen_la_confianza():
    netas = _rng(250, 0.0010, 0.0002)
    pocas = J.juzgar(_ops(netas), _ops(netas), meses=4, n_pruebas=1)
    muchas = J.juzgar(_ops(netas), _ops(netas), meses=4, n_pruebas=40)
    assert muchas.limite_inferior <= pocas.limite_inferior


def test_sin_operaciones_es_pendiente_y_n_pruebas_invalido_falla():
    assert J.juzgar([], [], meses=5, n_pruebas=4).estado == "pendiente"
    with pytest.raises(ValueError):
        J.juzgar([], [], meses=5, n_pruebas=0)


def test_caida_maxima_de_una_perdida_a_4x():
    op = R.Operacion("EURUSD", pd.Timestamp("2026-11-18"), pd.Timestamp("2026-11-18 10:00", tz="UTC"),
                     pd.Timestamp("2026-11-18 11:00", tz="UTC"), 1.0, 0.96, 0.0, "cierre")
    assert J.caida_maxima([op]) == pytest.approx(0.16)  # -4 % x 4 x 250 = -40 de 250
    assert J.caida_maxima([]) == 0.0


def test_el_bootstrap_es_reproducible():
    v = np.array([0.001, -0.0005, 0.002, 0.0003, 0.0011])
    assert J.limites_bootstrap(v, 0.99) == J.limites_bootstrap(v, 0.99)
