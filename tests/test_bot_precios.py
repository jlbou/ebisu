"""Pruebas de ebisu/precios.py con una fuente INVENTADA (sin red)."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from ebisu import precios as P

AHORA = datetime(2026, 10, 15, 20, 0, tzinfo=P.MADRID)  # jueves, despues del cierre


def serie(fechas: list[str], cierres: list[float], ajustados: list[float] | None = None,
          volumen: float = 1000.0) -> pd.DataFrame:
    idx = pd.to_datetime(fechas)
    return pd.DataFrame({"Close": cierres, "Adj Close": ajustados or cierres, "Volume": volumen}, index=idx)


def fuente_fija(datos: dict[str, pd.DataFrame]):
    def f(simbolo, desde):
        return datos[simbolo]
    return f


BASE = ["2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15"]


def todas(cierres=(10.0, 10.1, 10.2, 10.3), **kw) -> dict[str, pd.DataFrame]:
    return {s: serie(BASE, list(cierres), **kw) for _, s, _ in P.INSTRUMENTOS.values()}


def test_lista_cerrada_de_instrumentos():
    assert {i for i, _, _ in P.INSTRUMENTOS.values()} == {
        "IE00BK5BQT80", "IE000K1VI152", "IE00B579F325", "LU0290358497"}


def test_guarda_lo_cerrado_y_no_repite(tmp_path):
    f = tmp_path / "precios.csv"
    t, avisos = P.actualizar(f, AHORA, fuente_fija(todas()))
    assert len(t) == 4 and list(t.columns) == list(P.INSTRUMENTOS)
    assert not [a for a in avisos if a.tipo != "sin_volumen"]
    t2, avisos2 = P.actualizar(f, AHORA, fuente_fija(todas()))
    assert len(P.leer(f)) == 16 and t2.equals(t) and not avisos2


def test_no_guarda_hoy_antes_del_cierre_ni_sin_cierre(tmp_path):
    f = tmp_path / "precios.csv"
    pronto = datetime(2026, 10, 15, 12, 0, tzinfo=P.MADRID)
    datos = todas()
    datos["XEON.DE"].loc[pd.Timestamp("2026-10-14"), "Close"] = float("nan")
    t, _ = P.actualizar(f, pronto, fuente_fija(datos))
    assert pd.Timestamp("2026-10-15") not in t.index
    assert pd.isna(t.loc[pd.Timestamp("2026-10-14"), "monetario"])


def test_revision_de_la_fuente_no_cambia_lo_guardado(tmp_path):
    f = tmp_path / "precios.csv"
    P.actualizar(f, AHORA, fuente_fija(todas()))
    t, avisos = P.actualizar(f, AHORA, fuente_fija(todas(cierres=(10.0, 10.5, 10.2, 10.3))))
    assert t.loc[pd.Timestamp("2026-10-13"), "bolsa"] == pytest.approx(10.1)
    assert sum(a.tipo == "revision" for a in avisos) == 4


def test_salto_raro_no_se_guarda(tmp_path):
    f = tmp_path / "precios.csv"
    t, avisos = P.actualizar(f, AHORA, fuente_fija(todas(cierres=(10.0, 10.1, 12.0, 12.1))))
    assert len(t) == 2
    assert sum(a.tipo == "salto" for a in avisos) == 4


def test_ajustado_distinto_avisa(tmp_path):
    f = tmp_path / "precios.csv"
    _, avisos = P.actualizar(f, AHORA, fuente_fija(todas(ajustados=[10.0, 10.1, 10.2, 10.0])))
    assert sum(a.tipo == "ajuste" for a in avisos) == 4


def test_fuente_caida_no_tumba_el_dia(tmp_path):
    f = tmp_path / "precios.csv"
    datos = todas()

    def fuente(simbolo, desde):
        if simbolo == "SGLD.MI":
            raise ConnectionError("sin red")
        return datos[simbolo]

    t, avisos = P.actualizar(f, AHORA, fuente)
    assert t["oro"].isna().all() and t["bolsa"].notna().all()
    assert any(a.tipo == "fuente" and a.pieza == "oro" for a in avisos)


def test_vigilancia_sin_precio_y_sin_volumen(tmp_path):
    f = tmp_path / "precios.csv"
    tarde = datetime(2026, 10, 21, 20, 0, tzinfo=P.MADRID)  # 4 dias habiles despues del ultimo precio
    _, avisos = P.actualizar(f, tarde, fuente_fija(todas(volumen=0.0)))
    assert sum(a.tipo == "sin_precio" for a in avisos) == 4
    assert sum(a.tipo == "sin_volumen" for a in avisos) == 4
