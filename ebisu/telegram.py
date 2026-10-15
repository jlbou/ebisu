"""Telegram del bot: copia adaptada de `notify/telegram.py` de Ploutos (solo lectura de Ploutos; nada importado).

Dos reglas que no hay que deshacer:
1. **El token NUNCA sale en un error** (va en la URL de la API): todo texto de error pasa por `secretos.tapar`.
2. **`enviar` nunca lanza**: si Telegram esta caido, el bot sigue y el fallo queda en el resultado.
HTML de Telegram (solo hay que escapar < > &); si Telegram rechaza el HTML, se reenvia en texto plano.
"""

from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from ebisu.secretos import tapar

API = "https://api.telegram.org"
TIMEOUT = 20
MAX_LEN = 4096
RECORTE = "\n[...recortado]"


class TelegramError(Exception):
    pass


def llamar(token: str, metodo: str, params: dict[str, Any] | None = None, *, timeout: float = TIMEOUT,
           _open: Any = urllib.request.urlopen) -> Any:
    url = f"{API}/bot{token}/{metodo}"
    data = urllib.parse.urlencode(params or {}).encode() if params else None
    peticion = urllib.request.Request(url, data=data, headers={"User-Agent": "ebisu/0.1"})
    try:
        with _open(peticion, timeout=timeout) as r:
            respuesta = json.load(r)
    except urllib.error.HTTPError as exc:
        cuerpo = exc.read().decode("utf-8", "replace")[:300]
        try:
            descripcion = json.loads(cuerpo).get("description", cuerpo)
        except json.JSONDecodeError:
            descripcion = cuerpo
        raise TelegramError(f"HTTP {exc.code} en {metodo}: {tapar(descripcion, token)}") from None
    except Exception as exc:
        raise TelegramError(f"no se pudo contactar con Telegram en {metodo}: {tapar(str(exc), token)}") from None
    if not respuesta.get("ok"):
        raise TelegramError(f"{metodo} devolvio error: {tapar(str(respuesta.get('description')), token)}")
    return respuesta["result"]


@dataclass(frozen=True, slots=True)
class Envio:
    ok: bool
    detalle: str


def recortar(texto: str) -> str:
    return texto if len(texto) <= MAX_LEN else texto[: MAX_LEN - len(RECORTE)] + RECORTE


def a_texto_plano(texto_html: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", texto_html))


def enviar(token: str | None, chat_id: str | None, texto_html: str, *, timeout: float = TIMEOUT,
           _open: Any = urllib.request.urlopen) -> Envio:
    """Manda un aviso. NUNCA lanza."""
    if not token or not chat_id:
        return Envio(False, "sin TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en .env")

    def mandar(texto: str, modo: str | None) -> None:
        params = {"chat_id": chat_id, "text": recortar(texto), "disable_web_page_preview": "true"}
        if modo:
            params["parse_mode"] = modo
        llamar(token, "sendMessage", params, timeout=timeout, _open=_open)

    try:
        try:
            mandar(texto_html, "HTML")
        except TelegramError as exc:
            if "parse entities" not in str(exc):
                raise
            mandar(a_texto_plano(texto_html), None)
            return Envio(True, "enviado en texto plano (Telegram rechazo el HTML)")
    except TelegramError as exc:
        return Envio(False, str(exc))
    except Exception as exc:  # red de seguridad: nunca lanza
        return Envio(False, tapar(f"{type(exc).__name__}: {exc}", token))
    return Envio(True, "enviado")
