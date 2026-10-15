"""Latido para Healthchecks.io: copia adaptada de `notify/latido.py` de Ploutos.

Un bot caido no puede avisar de que se ha caido: lo avisa Healthchecks.io cuando le falta esta senyal. Se manda solo
cuando la vuelta del dia acaba bien; `fallo` avisa al momento. Nunca lanza, timeout corto, y la URL es un secreto (no
sale en ningun log).
"""

from __future__ import annotations

import logging
import urllib.request
from typing import Any

from ebisu.secretos import tapar

log = logging.getLogger("ebisu.latido")
TIMEOUT_S = 5.0


def _pedir(url: str | None, sufijo: str, _open: Any) -> bool | None:
    if not url:
        return None
    try:
        with _open(urllib.request.Request(url + sufijo, headers={"User-Agent": "ebisu/0.1"}), timeout=TIMEOUT_S) as r:
            return getattr(r, "status", 200) == 200
    except Exception as exc:
        log.warning("el latido no llego (%s)", tapar(f"{type(exc).__name__}: {exc}", url))
        return False


def todo_bien(url: str | None, _open: Any = urllib.request.urlopen) -> bool | None:
    """None = sin URL en el .env (desactivado)."""
    return _pedir(url, "", _open)


def fallo(url: str | None, _open: Any = urllib.request.urlopen) -> bool | None:
    return _pedir(url, "/fail", _open)
