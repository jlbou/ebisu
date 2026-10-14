"""La estrategia del bot es la del estudio 4, sin cambiar nada (docs/plan-bot-papel.md 10, B1)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from ebisu import estrategia as E

RAIZ = Path(__file__).resolve().parents[1]
ESTUDIO = RAIZ / "estudios" / "estudio4" / "simulador4.py"
sys.path.insert(0, str(ESTUDIO.parent))
import simulador4 as S  # noqa: E402


def sin_cabecera(texto: str) -> str:
    return texto[texto.index('"""', 3) + 3:]


def test_el_codigo_es_identico_al_del_estudio():
    bot = (RAIZ / "ebisu" / "estrategia.py").read_text(encoding="utf-8")
    assert sin_cabecera(bot) == sin_cabecera(ESTUDIO.read_text(encoding="utf-8"))


def test_mismo_resultado_con_datos_inventados():
    rng = np.random.default_rng(9)
    f = pd.bdate_range("2019-01-01", "2026-09-30")
    pz = pd.DataFrame({a: 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, len(f)))) for a in ("bolsa", "bonos", "oro")},
                      index=f)
    pz["monetario"] = 100 * np.cumprod(np.full(len(f), 1.0001))
    a = E.simular(pz, E.Variante("H1-M"), "2020-01-01", "2026-09-30")
    b = S.simular(pz, S.Variante("H1-M"), "2020-01-01", "2026-09-30")
    assert a.valor.equals(b.valor) and a.bolsillo == b.bolsillo and a.operaciones == b.operaciones


def test_huella_cambia_si_cambia_el_fichero(tmp_path):
    from ebisu.papel_huella import huella

    f = tmp_path / "x.py"
    f.write_text("a = 1\n", encoding="utf-8")
    h1 = huella(f)
    f.write_text("a = 2\n", encoding="utf-8")
    assert h1 != huella(f) and len(h1) == 64
