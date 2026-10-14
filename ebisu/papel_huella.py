"""Huella (SHA-256) de un fichero, para saber si la estrategia cambio durante el papel (docs/plan-bot-papel.md 10, B1)."""

from __future__ import annotations

import hashlib
from pathlib import Path

ESTRATEGIA = Path(__file__).resolve().parent / "estrategia.py"


def huella(fichero: Path = ESTRATEGIA) -> str:
    """Sobre el texto con saltos de linea normalizados: Windows (CRLF) y el VPS (LF) dan la misma huella."""
    texto = fichero.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()
