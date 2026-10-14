"""Las validaciones del estudio 1 como pruebas. Todas con datos INVENTADOS: no leen var/ ni salen a la red."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

E1 = Path(__file__).resolve().parents[1] / "estudios" / "estudio1"
E2 = Path(__file__).resolve().parents[1] / "estudios" / "estudio2"
H2R = Path(__file__).resolve().parents[1] / "estudios" / "h2reserva"
E3 = Path(__file__).resolve().parents[1] / "estudios" / "estudio3"
FIX = Path(__file__).resolve().parents[1] / "estudios" / "fixing"

CASOS = [
    ("validar.py",),
    ("juez.py", "--validar"),
    ("h2.py", "--validar"),
    ("medir.py", "--ensayo"),
    ("medir.py", "--ensayo-reserva"),
    ("e2:validar2.py",),
    ("e2:medir2.py", "--ensayo"),
    ("h2r:medir_h2.py", "--ensayo"),
    ("e3:diagnostico.py", "--validar"),
    ("e3:diagnostico.py", "--ensayo"),
    ("fix:rapido.py", "--validar"),
]


@pytest.mark.parametrize("args", CASOS, ids=[" ".join(c) for c in CASOS])
def test_validacion(args: tuple[str, ...]) -> None:
    prefijo, _, nombre = args[0].rpartition(":")
    base = {"": E1, "e2": E2, "h2r": H2R, "e3": E3, "fix": FIX}[prefijo]
    r = subprocess.run([sys.executable, str(base / nombre), *args[1:]], capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert "FALLA" not in r.stdout
