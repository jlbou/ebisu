"""Los secretos del bot, del `.env` del propietario (nunca en git; nunca se pide que se peguen).

Se lee el fichero como texto (CLAVE=valor), sin ejecutarlo y sin pasarlo a variables de entorno: asi ningun proceso
hijo (la IA) puede heredarlos (como la regla 19 de Ploutos). `tapar` quita los secretos de cualquier texto de error.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CLAVES = ("TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID", "HEALTHCHECK_EBISU", "CLAUDE_CODE_OAUTH_TOKEN")


@dataclass(frozen=True)
class Secretos:
    telegram_token: str | None = None
    telegram_chat_id: str | None = None
    healthcheck: str | None = None
    claude_token: str | None = None

    def todos(self) -> tuple[str, ...]:
        return tuple(s for s in (self.telegram_token, self.telegram_chat_id, self.healthcheck, self.claude_token) if s)


def leer(fichero: Path = RAIZ / ".env") -> Secretos:
    valores: dict[str, str] = {}
    if fichero.exists():
        for linea in fichero.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip().strip('"').strip("'")
    return Secretos(valores.get("TELEGRAM_TOKEN") or None, valores.get("TELEGRAM_CHAT_ID") or None,
                    valores.get("HEALTHCHECK_EBISU") or None, valores.get("CLAUDE_CODE_OAUTH_TOKEN") or None)


def tapar(texto: str, *secretos: str | None) -> str:
    out = texto
    for s in secretos:
        if s:
            out = out.replace(s, "***")
    return out
