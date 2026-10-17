"""El informe de revision (ebisu/revision.py), con el mundo inventado de test_bot_dia (sin red)."""

from __future__ import annotations

from datetime import date, datetime

from ebisu import precios, revision
from tests.test_bot_dia import Mundo, correr


def test_informe_de_unos_dias_buenos(tmp_path):
    m = Mundo()
    m.base = tmp_path
    for d in (13, 14, 15):
        correr(m, 2026, 10, d, 20, 5)
    lineas, graves = revision.informe(tmp_path, date(2026, 10, 13), datetime(2026, 10, 15, 22, 0, tzinfo=precios.MADRID))
    texto = "\n".join(lineas)
    assert graves == 0, texto
    assert "13/10: BIEN" in texto and "15/10: BIEN" in texto and "la IA responde" in texto
    assert "Si hoy" not in texto and "monetario" in texto


def test_un_dia_sin_vuelta_es_grave(tmp_path):
    m = Mundo()
    m.base = tmp_path
    correr(m, 2026, 10, 13, 20, 5)
    correr(m, 2026, 10, 15, 20, 5)
    lineas, graves = revision.informe(tmp_path, date(2026, 10, 13), datetime(2026, 10, 15, 22, 0, tzinfo=precios.MADRID))
    assert graves >= 1 and any("14/10: MAL" in x for x in lineas)


def test_el_informe_no_escribe_nada(tmp_path):
    m = Mundo()
    m.base = tmp_path
    correr(m, 2026, 10, 15, 20, 5)
    antes = {f.name: f.stat().st_mtime_ns for f in tmp_path.iterdir()}
    revision.informe(tmp_path, date(2026, 10, 15), datetime(2026, 10, 15, 22, 0, tzinfo=precios.MADRID))
    assert {f.name: f.stat().st_mtime_ns for f in tmp_path.iterdir()} == antes
