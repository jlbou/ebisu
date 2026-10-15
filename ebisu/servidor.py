"""El servidor del panel (P5; B7; docs/plan-bot-papel.md): pequenyo, sin dependencias, SOLO por Tailscale.

- Escucha solo en la IP de Tailscale de esta maquina (100.x.y.z), como el panel de Ploutos; si no la hay, no arranca.
  Nunca en todas las interfaces.
- GET: la pagina (`var/bot/panel.html`), `panel.js` y el icono. Nada mas (sin rutas de ficheros: sin recorrer
  carpetas).
- POST /control: pausar o reanudar. Solo con la cabecera `X-Ebisu-Panel: 1` y, si trae Origin, el del propio panel
  (otra pagina no puede pulsar los botones). Se apunta en `control.json` con su hora; en papel no actua.
- Cabeceras de seguridad: CSP solo propia, sin marcos, sin adivinar tipos, sin Referer.
- **Solo responde si la cabecera Host es la del propio panel** (su IP:puerto o su nombre de Tailscale): asi una web de
  fuera no puede leerlo ni pulsar los botones apuntando su dominio a esta IP (DNS rebinding).

    python -m ebisu.servidor [--host 100.x.y.z] [--puerto 8611]
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ebisu import panel, precios

RAIZ = Path(__file__).resolve().parents[1]
VAR = RAIZ / "var" / "bot"
ESTATICOS = {"/panel.js": (Path(__file__).with_name("panel.js"), "text/javascript; charset=utf-8"),
             "/favicon.svg": (RAIZ / "assets" / "logo" / "favicon.svg", "image/svg+xml")}
CABECERAS = {"Content-Security-Policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                                        "script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
             "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
             "Cache-Control": "no-store"}
MAX_CUERPO = 1024
TAILSCALE = ipaddress.ip_network("100.64.0.0/10")


def ip_tailscale() -> str | None:
    try:
        salida = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    for linea in salida.split():
        try:
            if ipaddress.ip_address(linea) in TAILSCALE:
                return linea
        except ValueError:
            continue
    return None


def permitido(cabeceras: dict[str, str]) -> bool:
    if cabeceras.get("x-ebisu-panel") != "1":
        return False
    origen = cabeceras.get("origin")
    return origen is None or urlparse(origen).netloc == cabeceras.get("host")


def aplicar(base: Path, accion: str, ahora: datetime) -> dict:
    f = base / "control.json"
    c = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"pausa": False, "historial": []}
    if accion not in ("pausa", "reanudar"):
        raise ValueError("accion desconocida")
    if (accion == "pausa") == bool(c.get("pausa")):
        raise ValueError("ya estaba asi")
    c["pausa"] = accion == "pausa"
    c["historial"] = (c.get("historial", []) + [{"accion": accion, "hora": ahora.isoformat(timespec="seconds")}])[-100:]
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, f)
    return c


def manejador(base: Path, hosts: set[str] | None = None):
    """hosts = valores permitidos de la cabecera Host (None solo en pruebas locales)."""
    class Manejador(BaseHTTPRequestHandler):
        server_version = "ebisu"
        sys_version = ""

        def _responder(self, codigo: int, cuerpo: bytes, tipo: str = "text/plain; charset=utf-8") -> None:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            for k, v in CABECERAS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(cuerpo)

        def _host_valido(self) -> bool:
            return hosts is None or (self.headers.get("Host") or "").lower() in hosts

        def do_GET(self) -> None:  # noqa: N802
            if not self._host_valido():
                return self._responder(421, b"host no permitido")
            ruta = urlparse(self.path).path
            if ruta == "/":
                f = base / "panel.html"
                if not f.exists():
                    panel.escribir(base, datetime.now(precios.MADRID))
                self._responder(200, f.read_bytes(), "text/html; charset=utf-8")
            elif ruta in ESTATICOS:
                fichero, tipo = ESTATICOS[ruta]
                self._responder(200, fichero.read_bytes(), tipo)
            else:
                self._responder(404, b"no existe")

        def do_POST(self) -> None:  # noqa: N802
            try:
                n = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                return self._responder(400, b"longitud invalida")
            if n < 0 or n > MAX_CUERPO:
                return self._responder(413, b"demasiado grande")
            # El cuerpo se lee ANTES de rechazar: un rechazo sin leerlo puede cortar la conexion antes de la respuesta.
            cuerpo = self.rfile.read(n)
            if not self._host_valido():
                return self._responder(421, b"host no permitido")
            if urlparse(self.path).path != "/control":
                return self._responder(404, b"no existe")
            if not permitido({k.lower(): v for k, v in self.headers.items()}):
                return self._responder(403, b"no permitido")
            try:
                accion = json.loads(cuerpo or b"{}").get("accion")
                aplicar(base, accion, datetime.now(precios.MADRID))
                panel.escribir(base, datetime.now(precios.MADRID))
            except (ValueError, AttributeError) as exc:
                return self._responder(409, str(exc).encode())
            self._responder(200, b"ok")

        def log_message(self, formato, *args) -> None:  # sin rutas ni IP en los registros
            pass

    return Manejador


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", help="IP de Tailscale (por defecto, la de esta maquina)")
    ap.add_argument("--puerto", type=int, default=8611)
    ap.add_argument("--nombre", help="nombre de la maquina en Tailscale (MagicDNS), si se entra por nombre")
    a = ap.parse_args()
    host = a.host or ip_tailscale()
    if not host or ipaddress.ip_address(host) not in TAILSCALE:
        raise SystemExit("Sin IP de Tailscale: el panel no arranca (solo se ve por Tailscale).")
    hosts = {f"{host}:{a.puerto}"} | ({f"{a.nombre.lower()}:{a.puerto}"} if a.nombre else set())
    ThreadingHTTPServer((host, a.puerto), manejador(VAR, hosts)).serve_forever()


if __name__ == "__main__":
    main()
