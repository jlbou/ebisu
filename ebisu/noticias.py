"""Titulares para la IA (P3; docs/plan-bot-papel.md 9): copia adaptada de `data/medios/rss.py` de Ploutos.

Fuentes (comprobadas el 15/10/2026, todas responden): comunicados del BCE y de la Fed, y cuatro medios economicos.

TEXTO DE FUERA, NO CONFIABLE:
- se rechaza un documento con `<!DOCTYPE` o `<!ENTITY` (una bomba de entidades tumbaria la memoria), de mas de
  `MAX_BYTES` o mal formado;
- los titulos se guardan como texto plano, recortados; para la IA son datos, nunca instrucciones.
NUNCA LANZA: una fuente que falla se apunta y las demas siguen.
"""

from __future__ import annotations

import csv
import html
import io
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

USER_AGENT = "Mozilla/5.0 (compatible; ebisu-noticias/0.1)"
TIMEOUT_S = 15.0
MAX_BYTES = 2_000_000
MAX_TITULO = 300
ATOM = "{http://www.w3.org/2005/Atom}"
DC = "{http://purl.org/dc/elements/1.1/}"
FUENTES = {
    "bce": "https://www.ecb.europa.eu/rss/press.html",
    "fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ft": "https://www.ft.com/markets?format=rss",
    "cnbc": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "marketwatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "expansion": "https://e00-expansion.uecdn.es/rss/mercados.xml",
}
CAMPOS = ["id", "fuente", "titulo", "publicado", "visto"]

_ETIQUETAS = re.compile(r"<[^>]*>")
_ESPACIOS = re.compile(r"\s+")
_PELIGROSO = re.compile(rb"<!\s*(DOCTYPE|ENTITY)", re.I)


@dataclass(frozen=True, slots=True)
class Titular:
    fuente: str
    guid: str
    titulo: str
    publicado: datetime | None

    @property
    def id(self) -> str:
        return f"{self.fuente}:{self.guid}"


def texto_plano(valor: str | None, maximo: int) -> str:
    if not valor:
        return ""
    return _ESPACIOS.sub(" ", html.unescape(_ETIQUETAS.sub(" ", valor))).strip()[:maximo]


def fecha(valor: str | None) -> datetime | None:
    if not valor or not valor.strip():
        return None
    try:
        dt = parsedate_to_datetime(valor.strip())
    except (TypeError, ValueError, IndexError):
        try:
            dt = datetime.fromisoformat(valor.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _texto(padre: ET.Element, etiqueta: str) -> str | None:
    """Todo el texto del elemento, tambien el de dentro de etiquetas (`findtext` se queda en la primera)."""
    el = padre.find(etiqueta)
    return None if el is None else "".join(el.itertext())


def interpretar(cuerpo: bytes, fuente: str) -> tuple[list[Titular], str | None]:
    """El documento de un feed -> titulares, o el error. Puro: sin red."""
    if len(cuerpo) > MAX_BYTES:
        return [], f"{fuente}: documento demasiado grande"
    if _PELIGROSO.search(cuerpo):
        return [], f"{fuente}: documento con DOCTYPE o ENTITY, rechazado"
    try:
        raiz = ET.fromstring(cuerpo)
    except ET.ParseError as exc:
        return [], f"{fuente}: XML mal formado ({exc})"
    out = []
    for item in raiz.iter("item"):  # RSS 2.0
        titulo = texto_plano(_texto(item, "title"), MAX_TITULO)
        guid = texto_plano(item.findtext("guid"), 500) or texto_plano(item.findtext("link"), 500) or titulo
        if titulo:
            out.append(Titular(fuente, guid, titulo, fecha(item.findtext("pubDate") or item.findtext(f"{DC}date"))))
    for e in raiz.iter(f"{ATOM}entry"):  # Atom
        titulo = texto_plano(_texto(e, f"{ATOM}title"), MAX_TITULO)
        guid = texto_plano(e.findtext(f"{ATOM}id"), 500) or titulo
        if titulo:
            out.append(Titular(fuente, guid, titulo, fecha(e.findtext(f"{ATOM}updated") or e.findtext(f"{ATOM}published"))))
    return out, None


def bajar(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=TIMEOUT_S) as r:
        return r.read(MAX_BYTES + 1)


def recoger(fichero: Path, ahora: datetime, _bajar: Callable[[str], bytes] = bajar) -> tuple[int, list[str]]:
    """Lee las fuentes y anyade los titulares nuevos. Devuelve (nuevos, errores). Nunca lanza."""
    vistos = set()
    if fichero.exists():
        with fichero.open(encoding="utf-8") as f:
            vistos = {fila["id"] for fila in csv.DictReader(f)}
    nuevos, errores = [], []
    for nombre, url in FUENTES.items():
        try:
            titulares, error = interpretar(_bajar(url), nombre)
        except Exception as exc:
            titulares, error = [], f"{nombre}: {type(exc).__name__}"
        if error:
            errores.append(error)
        for t in titulares:
            if t.id not in vistos:
                vistos.add(t.id)
                nuevos.append({"id": t.id, "fuente": t.fuente, "titulo": t.titulo,
                               "publicado": t.publicado.isoformat() if t.publicado else "",
                               "visto": ahora.isoformat(timespec="seconds")})
    if nuevos:
        try:
            fichero.parent.mkdir(parents=True, exist_ok=True)
            texto = io.StringIO()
            w = csv.DictWriter(texto, fieldnames=CAMPOS, lineterminator="\n")
            if not fichero.exists():
                w.writeheader()
            w.writerows(nuevos)
            with fichero.open("a", newline="", encoding="utf-8") as f:
                f.write(texto.getvalue())
                f.flush()
                os.fsync(f.fileno())
        except OSError as exc:
            errores.append(f"no se pudieron guardar los titulares: {type(exc).__name__}")
            return 0, errores
    return len(nuevos), errores


def del_periodo(fichero: Path, desde: datetime, hasta: datetime, maximo: int = 150) -> list[dict]:
    """Titulares vistos entre dos momentos (por fecha de cuando se vieron), los mas recientes primero."""
    if not fichero.exists():
        return []
    with fichero.open(encoding="utf-8") as f:
        filas = [r for r in csv.DictReader(f) if desde <= datetime.fromisoformat(r["visto"]) <= hasta]
    return sorted(filas, key=lambda r: r["visto"], reverse=True)[:maximo]
