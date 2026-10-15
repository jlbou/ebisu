"""Comandos de Telegram del bot en papel (P4): solo `/estado` y `/detalle`. Pausar y reanudar, desde el panel.

- Solo responde al chat del propietario (TELEGRAM_CHAT_ID); lo demas se ignora en silencio.
- Solo LEE el estado que deja la vuelta del dia (`var/bot/estado.json`): no cambia nada del papel.
- El servicio escucha con espera larga (getUpdates); nunca se cae por un error de red: espera y vuelve a intentar.

    python -m ebisu.comandos
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from ebisu import mensajes as m
from ebisu import secretos, telegram

VAR = Path(__file__).resolve().parents[1] / "var" / "bot"
log = logging.getLogger("ebisu.comandos")
AYUDA = "Comandos: /estado (resumen) y /detalle (la version larga). Pausar y reanudar, desde el panel."


def _estado(base: Path) -> dict:
    f = base / "estado.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def estado_texto(e: dict) -> str:
    if not e.get("valor_eur"):
        return f"{m.CABECERA}\nEl papel aun no ha empezado (ultima vuelta: {m.e(e.get('ultima_vuelta', 'ninguna'))})."
    lineas = [f"{m.CABECERA} · /estado",
              f"Valor: {m.eur(e['valor_eur'])} · VWCE mantenido: {m.eur(e['referencia_eur'])}",
              f"Peor caída: {m.pct(e['caida'])} · Datos hasta el {m.e(e['papel_hasta'])}"]
    for p, w in e.get("pesos", {}).items():
        lineas.append(f"• {m.e(m.NOMBRES[p])}: {e.get('puntos', {}).get(p, 0)}/4 · {m.pct(w)}")
    graves = [i for i in e.get("incidencias", []) if i["grave"]]
    lineas.append(f"Salud: {'⚠️ ' + str(len(graves)) + ' incidencia(s) grave(s)' if graves else 'todo bien'}")
    return "\n".join(lineas)


def detalle_texto(e: dict) -> str:
    if not e.get("valor_eur"):
        return estado_texto(e)
    lineas = [estado_texto(e).replace("/estado", "/detalle"),
              f"Si lo vendiera todo hoy (impuestos incluidos): {m.eur(e['si_vende_hoy_eur'])}"]
    ia = e.get("ia") or {}
    lineas.append(f"La IA ({m.e(ia.get('senyal', '-'))}): {m.e(ia.get('explicacion') or ia.get('motivo') or 'sin respuesta')}")
    for pieza, motivo in ia.get("frenos", []):
        lineas.append(f"  · Frenaría {m.e(m.NOMBRES.get(pieza, pieza))} (en sombra): {m.e(motivo)}")
    ops = e.get("operaciones", [])[-8:]
    if ops:
        lineas.append("Últimas operaciones:")
        for o in ops:
            lineas.append(f"  · {m.e(o['fecha'])} {m.e(m.NOMBRES[o['pieza']])}: {m.pct(o['antes'])} → {m.pct(o['despues'])}")
    for i in e.get("incidencias", []):
        lineas.append(f"{'⚠️' if i['grave'] else '·'} {m.e(i['tipo'])}: {m.e(i['texto'])}")
    return "\n".join(lineas)


def responder(texto: str, chat: str, chat_propietario: str | None, base: Path) -> str | None:
    """La respuesta a un mensaje, o None si no se responde (otro chat o no es un comando)."""
    if not chat_propietario or str(chat) != str(chat_propietario):
        return None
    orden = (texto or "").strip().split()[0].split("@")[0].lower() if (texto or "").strip() else ""
    if orden == "/estado":
        return estado_texto(_estado(base))
    if orden == "/detalle":
        return detalle_texto(_estado(base))
    if orden.startswith("/"):
        return AYUDA
    return None


def escuchar(base: Path = VAR, _llamar: Any = telegram.llamar, _dormir: Any = time.sleep, vueltas: int | None = None) -> None:
    s = secretos.leer()
    if not s.telegram_token:
        raise SystemExit("sin TELEGRAM_TOKEN en .env")
    offset = None
    n = 0
    while vueltas is None or n < vueltas:
        n += 1
        try:
            params = {"timeout": 50, "allowed_updates": json.dumps(["message"])}
            if offset is not None:
                params["offset"] = offset
            for u in _llamar(s.telegram_token, "getUpdates", params, timeout=60):
                offset = u["update_id"] + 1
                msg = u.get("message") or {}
                r = responder(msg.get("text", ""), str((msg.get("chat") or {}).get("id")), s.telegram_chat_id, base)
                if r:
                    telegram.enviar(s.telegram_token, s.telegram_chat_id, r)
        except Exception as exc:
            log.warning("comandos: %s", secretos.tapar(f"{type(exc).__name__}: {exc}", *s.todos()))
            _dormir(30)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    escuchar()
