"""Cola de avisos (idea de `notify/outbox.py` de Ploutos): se apuntan primero y se mandan despues.

- Cada aviso tiene una clave unica: el mismo aviso no se apunta dos veces (si el dia se rehace, no se repite).
- `enviar_pendientes` NUNCA lanza; para en el primer fallo (Telegram caido): lo que queda sale la vuelta siguiente.
- Un aviso de mas de `MAX_EDAD` sin salir se descarta: llegaria como si fuera de ahora.
Guardado: JSON en var/ (pequenyo: unos pocos avisos al mes).
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path

MAX_EDAD = timedelta(hours=48)
MAX_POR_VUELTA = 10


def _leer(fichero: Path) -> dict:
    if not fichero.exists():
        return {"pendientes": [], "enviados": []}
    return json.loads(fichero.read_text(encoding="utf-8"))


def _escribir(fichero: Path, datos: dict) -> None:
    fichero.parent.mkdir(parents=True, exist_ok=True)
    tmp = fichero.with_suffix(".tmp")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, fichero)  # cambio de golpe: nunca a medias


def apuntar(fichero: Path, clave: str, texto: str, ahora: datetime) -> bool:
    """True si se apunta; False si ya estaba (pendiente o enviado)."""
    d = _leer(fichero)
    if clave in d["enviados"] or any(p["clave"] == clave for p in d["pendientes"]):
        return False
    d["pendientes"].append({"clave": clave, "texto": texto, "creado": ahora.isoformat()})
    _escribir(fichero, d)
    return True


def enviar_pendientes(fichero: Path, mandar: Callable[[str], bool], ahora: datetime) -> tuple[int, int]:
    """Manda los pendientes en orden. Devuelve (enviados, descartados por viejos). Nunca lanza."""
    try:
        d = _leer(fichero)
    except (OSError, json.JSONDecodeError):
        return 0, 0
    enviados = descartados = 0
    quedan = []
    for i, p in enumerate(d["pendientes"]):
        if ahora - datetime.fromisoformat(p["creado"]) > MAX_EDAD:
            descartados += 1
            continue
        if enviados >= MAX_POR_VUELTA:
            quedan += d["pendientes"][i:]
            break
        try:
            ok = mandar(p["texto"])
        except Exception:
            ok = False
        if not ok:
            quedan += d["pendientes"][i:]
            break
        d["enviados"].append(p["clave"])
        enviados += 1
    d["pendientes"] = quedan
    d["enviados"] = d["enviados"][-2000:]
    try:
        _escribir(fichero, d)
    except OSError:
        pass
    return enviados, descartados
