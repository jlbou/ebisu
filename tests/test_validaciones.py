"""Las validaciones del estudio 1 como pruebas. Todas con datos INVENTADOS: no leen var/ ni salen a la red."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

E1 = Path(__file__).resolve().parents[1] / "estudios" / "estudio1"

CASOS = [
    ("validar.py",),
    ("juez.py", "--validar"),
    ("h2.py", "--validar"),
    ("medir.py", "--ensayo"),
    ("medir.py", "--ensayo-reserva"),
]


@pytest.mark.parametrize("args", CASOS, ids=[" ".join(c) for c in CASOS])
def test_validacion(args: tuple[str, ...]) -> None:
    r = subprocess.run([sys.executable, str(E1 / args[0]), *args[1:]], capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert "FALLA" not in r.stdout
