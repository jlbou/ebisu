"""Pruebas del panel y de su servidor, con el mundo inventado de test_bot_dia (sin red)."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from ebisu import servidor
from tests.test_bot_dia import Mundo, correr


@pytest.fixture
def mundo(tmp_path):
    from ebisu import dia

    m = Mundo()
    m.base = tmp_path
    dia.empezar(tmp_path, "2026-09-30")
    correr(m, 2026, 9, 30, 20, 0)
    correr(m, 2026, 10, 1, 20, 0)
    return m


def test_el_panel_tiene_las_secciones_y_nunca_el_nombre_del_modelo(mundo):
    pagina = (mundo.base / "panel.html").read_text(encoding="utf-8")
    for s in ("Resumen", "1. Valor frente al indexado", "2. Cada pieza con sus 4 medias", "3. Operaciones",
              "4. Historial de la IA", "5. Con y sin la IA", "6. Hacienda"):
        assert s in pagina
    assert "claude" not in pagina.lower() and "Pausar" in pagina
    assert pagina.count("<svg") >= 4  # logo + las 3 piezas (el valor necesita al menos 2 dias de papel)


@pytest.fixture
def web(mundo):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.manejador(mundo.base))
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}", mundo
    srv.shutdown()


def pedir(url, metodo="GET", cabeceras=None, cuerpo=None):
    r = urllib.request.Request(url, method=metodo, headers=cabeceras or {}, data=cuerpo)
    try:
        with urllib.request.urlopen(r, timeout=10) as x:
            return x.status, x.headers, x.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read()


def test_servidor_pagina_y_cabeceras(web):
    url, _ = web
    codigo, cab, cuerpo = pedir(url + "/")
    assert codigo == 200 and "frame-ancestors 'none'" in cab["Content-Security-Policy"] and b"Ebisu" in cuerpo
    assert pedir(url + "/../../.env")[0] == 404 and pedir(url + "/var/bot/estado.json")[0] == 404


def test_botones_solo_desde_el_panel(web):
    url, m = web
    cuerpo = json.dumps({"accion": "pausa"}).encode()
    assert pedir(url + "/control", "POST", {"Content-Type": "application/json"}, cuerpo)[0] == 403
    otra = {"X-Ebisu-Panel": "1", "Origin": "https://malo.example"}
    assert pedir(url + "/control", "POST", otra, cuerpo)[0] == 403
    assert pedir(url + "/control", "POST", {"X-Ebisu-Panel": "1"}, cuerpo)[0] == 200
    assert json.loads((m.base / "control.json").read_text(encoding="utf-8"))["pausa"] is True
    assert pedir(url + "/control", "POST", {"X-Ebisu-Panel": "1"}, cuerpo)[0] == 409  # ya estaba en pausa
    assert "Reanudar" in (m.base / "panel.html").read_text(encoding="utf-8")


def test_la_pausa_no_cambia_el_papel(web):
    url, m = web
    antes = json.loads((m.base / "estado.json").read_text(encoding="utf-8"))["operaciones"]
    pedir(url + "/control", "POST", {"X-Ebisu-Panel": "1"}, json.dumps({"accion": "pausa"}).encode())
    e = correr(m, 2026, 10, 2, 20, 0)
    assert e["operaciones"][: len(antes)] == antes


def test_el_servidor_no_arranca_fuera_de_tailscale(monkeypatch):
    monkeypatch.setattr(servidor, "ip_tailscale", lambda: None)
    monkeypatch.setattr("sys.argv", ["servidor"])
    with pytest.raises(SystemExit):
        servidor.main()
    monkeypatch.setattr("sys.argv", ["servidor", "--host", "0.0.0.0"])
    with pytest.raises(SystemExit):
        servidor.main()
