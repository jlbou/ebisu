"""Los ficheros de instalacion del bot (docs/plan-bot-papel.md 10): aislados de Ploutos y sin datos privados."""

from __future__ import annotations

import re
from pathlib import Path

DEPLOY = Path(__file__).resolve().parents[1] / "deploy"
SERVICIOS = ["ebisu-dia.service", "ebisu-comandos.service", "ebisu-panel.service", "ebisu-copia.service"]


def sin_comentarios(f: Path) -> str:
    """El fichero sin las lineas de comentario (pueden nombrar a Ploutos para decir que no se toca)."""
    return "\n".join(x for x in f.read_text(encoding="utf-8").splitlines() if not x.lstrip().startswith("#"))


def test_servicios_aislados():
    for s in SERVICIOS:
        t = sin_comentarios(DEPLOY / s)
        for linea in ("User=ebisu", "NoNewPrivileges=true", "ProtectSystem=strict", "ProtectHome=true",
                      "InaccessiblePaths=-/opt/ploutos"):
            assert linea in t, f"{s}: falta {linea}"
        assert "ploutos" not in t.replace("InaccessiblePaths=-/opt/ploutos", "").lower(), s


def test_el_panel_no_escucha_en_todas_las_interfaces():
    t = (DEPLOY / "ebisu-panel.service").read_text(encoding="utf-8")
    assert "0.0.0.0" not in t and "--host" not in t  # la IP la saca de Tailscale


def test_sin_ips_ni_secretos_en_los_ficheros_de_instalacion():
    for f in DEPLOY.iterdir():
        if f.suffix == ".lock":
            continue
        t = f.read_text(encoding="utf-8")
        ips = [ip for ip in re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", t) if not ip.startswith("100.64.")]
        assert not ips, f"{f.name}: {ips}"
        assert not re.search(r"(TOKEN|CHAT_ID|HEALTHCHECK_EBISU)\s*=\s*\S", t), f.name


def test_instalar_no_toca_ploutos():
    t = sin_comentarios(DEPLOY / "instalar.sh")
    assert "/opt/ploutos" not in t and "systemctl" in t
    assert all(u.startswith("ebisu-") for u in re.findall(r"(\S+\.(?:service|timer))", t))


def test_la_ia_propia_es_la_version_verificada():
    from ebisu import ia
    t = sin_comentarios(DEPLOY / "instalar-ia.sh")
    assert f'VERSION_IA="{ia.VERSION_VERIFICADA}"' in t and "VALIDSIG" in t and "sha256sum" in t
    assert "/opt/ploutos" not in t and "/home/" not in t  # no depende de ninguna otra instalacion
    assert ia.PROPIO.relative_to(ia.RAIZ).as_posix() == "bin/claude"
    assert 'bash "${APP_DIR}/deploy/instalar-ia.sh"' in (DEPLOY / "instalar.sh").read_text(encoding="utf-8")


def test_las_dependencias_del_bot_estan_fijadas():
    lineas = [x for x in (DEPLOY / "requirements-bot.lock").read_text(encoding="utf-8").splitlines()
              if x and not x.startswith("#")]
    assert lineas and all(re.fullmatch(r"[A-Za-z0-9_.\-]+==[\w.]+", x) for x in lineas)
    assert not any(x.lower().startswith(("scikit-learn", "scipy")) for x in lineas)
