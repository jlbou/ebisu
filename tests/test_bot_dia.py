"""La vuelta del dia de principio a fin, con todo inventado (precios, titulares, IA, Telegram, latido)."""

from __future__ import annotations

import json
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from ebisu import dia, ia, precios, secretos

M = precios.MADRID


def precios_inventados() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(3)
    f = pd.bdate_range("2019-01-01", "2026-12-31")
    out = {}
    for _, simbolo, _ in precios.INSTRUMENTOS.values():
        drift = 0.0001 if simbolo == "XEON.DE" else 0.0004
        sd = 0.0001 if simbolo == "XEON.DE" else 0.008
        c = 50 * np.exp(np.cumsum(rng.normal(drift, sd, len(f))))
        out[simbolo] = pd.DataFrame({"Close": c, "Adj Close": c, "Volume": 1000.0}, index=f)
    return out


RSS = b"<rss><channel><item><title>Titular</title><guid>g1</guid></item></channel></rss>"


class Mundo:
    def __init__(self):
        self.datos = precios_inventados()
        self.enviados: list[str] = []
        self.ia: list[dict] = []
        self.latidos: list[str] = []

    def dep(self) -> dia.Dependencias:
        def preguntar(mes, titulares, compras, token):
            self.ia.append(mes)
            frenos = (("oro", "riesgo inventado"),) if "oro" in compras else ()
            return ia.Respuesta(True, "ok", "La regla compra lo que sube.", frenos)

        return dia.Dependencias(
            fuente_precios=lambda s, d: self.datos[s], bajar_rss=lambda url: RSS, preguntar_ia=preguntar,
            mandar=lambda t: self.enviados.append(t) or True,
            latido_ok=lambda u: self.latidos.append("ok"), latido_fallo=lambda u: self.latidos.append("fallo"),
            secretos=secretos.Secretos("t", "1", "https://hc", "tok"))


@pytest.fixture
def mundo(tmp_path):
    m = Mundo()
    m.base = tmp_path
    dia.empezar(tmp_path, "2026-09-30")
    return m


def correr(m: Mundo, *fecha) -> dict:
    return dia.vuelta(datetime(*fecha, tzinfo=M), m.base, m.dep())


def test_no_se_puede_empezar_dos_veces(mundo):
    with pytest.raises(SystemExit):
        dia.empezar(mundo.base, "2026-10-30")


def test_un_mes_entero(mundo):
    e = correr(mundo, 2026, 9, 30, 20, 0)  # dia de la senyal: la IA, sin operaciones todavia
    assert len(mundo.ia) == 1 and mundo.ia[0]["senyal"] == "2026-09-30"
    assert e["ultima_senyal_tratada"] == "2026-09-30" and "papel_hasta" not in e
    assert mundo.latidos == ["ok"]
    e = correr(mundo, 2026, 10, 1, 20, 0)  # se ejecuta: operaciones y resumen del mes
    assert e["papel_hasta"] == "2026-10-01" and e["operaciones"]
    textos = "\n".join(mundo.enviados)
    assert "Operaciones del 01/10/2026" in textos and "resumen de septiembre" in textos
    assert len(mundo.ia) == 1  # la IA no se repite
    n = len(mundo.enviados)
    correr(mundo, 2026, 10, 1, 21, 0)  # rehacer el dia no repite avisos
    assert len(mundo.enviados) == n
    correr(mundo, 2026, 10, 4, 20, 0)  # domingo: todo bien
    assert "todo bien" in mundo.enviados[-1]


def test_freno_de_la_ia_se_avisa_y_se_apunta(mundo):
    correr(mundo, 2026, 9, 30, 20, 0)
    diario = (mundo.base / "ia_diario.jsonl").read_text(encoding="utf-8").splitlines()
    fila = json.loads(diario[0])
    assert fila["ok"] and fila["senyal"].startswith("2026-09-30")
    if "oro" in fila["compras"]:
        assert any("frenaría la compra de Oro" in t for t in mundo.enviados)


def test_senyal_sin_vuelta_es_incidencia(mundo):
    correr(mundo, 2026, 10, 1, 20, 0)  # el bot no corrio el 30/09
    assert any("senyal_sin_vuelta" in t for t in mundo.enviados)
    assert len(mundo.ia) == 1  # la IA de la senyal del 30/09 se hace igualmente (tarde)


def test_si_revienta_avisa_late_fallo_y_no_ensenya_secretos(mundo):
    dep = mundo.dep()
    dep.secretos = secretos.Secretos("t", "1", "https://hc", "SECRETO-XYZ")

    def ia_rota(*a, **k):
        raise RuntimeError("fallo con SECRETO-XYZ dentro")

    dep.preguntar_ia = ia_rota
    assert dia.principal(datetime(2026, 9, 30, 20, 0, tzinfo=M), mundo.base, dep) == 1
    assert mundo.latidos[-1] == "fallo" and "Incidencia grave" in mundo.enviados[-1]
    assert "SECRETO-XYZ" not in mundo.enviados[-1]
    assert "SECRETO-XYZ" not in (mundo.base / "vueltas.csv").read_text(encoding="utf-8")


# --- Comandos -----------------------------------------------------------------------------------------------------

def test_comandos_solo_del_propietario_y_solo_leen(mundo):
    from ebisu import comandos

    correr(mundo, 2026, 9, 30, 20, 0)
    correr(mundo, 2026, 10, 1, 20, 0)
    antes = (mundo.base / "estado.json").read_text(encoding="utf-8")
    est = comandos.responder("/estado", "1", "1", mundo.base)
    det = comandos.responder("/detalle@EbisuBot", "1", "1", mundo.base)
    assert "Valor:" in est and "VWCE mantenido" in est
    assert "La IA" in det and "Últimas operaciones" in det and "claude" not in det.lower()
    assert comandos.responder("/estado", "999", "1", mundo.base) is None  # otro chat: nada
    assert comandos.responder("/pausa", "1", "1", mundo.base) == comandos.AYUDA  # la pausa no existe aqui
    assert comandos.responder("hola", "1", "1", mundo.base) is None
    assert (mundo.base / "estado.json").read_text(encoding="utf-8") == antes


def test_comandos_antes_de_empezar(tmp_path):
    from ebisu import comandos

    assert "aun no ha empezado" in comandos.responder("/estado", "1", "1", tmp_path)
