"""Las validaciones del estudio 1 como pruebas. Todas con datos INVENTADOS: no leen var/ ni salen a la red."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

E1 = Path(__file__).resolve().parents[1] / "estudios" / "estudio1"
E2 = Path(__file__).resolve().parents[1] / "estudios" / "estudio2"

CASOS = [
    ("validar.py",),
    ("juez.py", "--validar"),
    ("h2.py", "--validar"),
    ("medir.py", "--ensayo"),
    ("medir.py", "--ensayo-reserva"),
    ("e2:validar2.py",),
    ("e2:medir2.py", "--ensayo"),
]


@pytest.mark.parametrize("args", CASOS, ids=[" ".join(c) for c in CASOS])
def test_validacion(args: tuple[str, ...]) -> None:
    base, nombre = (E2, args[0][3:]) if args[0].startswith("e2:") else (E1, args[0])
    r = subprocess.run([sys.executable, str(base / nombre), *args[1:]], capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert "FALLA" not in r.stdout
