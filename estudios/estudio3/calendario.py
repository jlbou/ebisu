"""Calendario de eventos programados del estudio 3 (docs/plan-estudio-3.md, decision 4 y anexo; T1 y T2).

Solo eventos que se sabian de antemano: reuniones PROGRAMADAS de los bancos centrales (no las de urgencia), el informe
de empleo de EE. UU. y las elecciones y referendums nacionales. Cada fuente se descarga una vez a
var/estudio3/fuentes/ y se interpreta aqui; el resultado va a estudios/estudio3/eventos.csv (en git: son datos
publicos y asi se puede revisar fila a fila).

Columnas: fecha (dia del anuncio, hora local del banco), divisa, evento, fuente.

Uso: .venv/Scripts/python.exe estudios/estudio3/calendario.py [banco ...]
"""

from __future__ import annotations

import argparse
import html
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
FUENTES = RAIZ / "var" / "estudio3" / "fuentes"
SALIDA = AQUI / "eventos.csv"
DESDE, HASTA = 2003, 2026
MESES = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


def bajar(url: str, nombre: str) -> str:
    """Descarga una pagina una sola vez (cache en var/) y devuelve su texto."""
    f = FUENTES / nombre
    if not f.exists():
        FUENTES.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ebisu-estudio)"})
        with urllib.request.urlopen(req, timeout=90) as r:
            f.write_bytes(r.read())
        time.sleep(1)
    return f.read_text(encoding="utf-8", errors="replace")


def texto(h: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def fila(fecha: pd.Timestamp, divisa: str, evento: str, fuente: str) -> dict:
    return {"fecha": fecha.date().isoformat(), "divisa": divisa, "evento": evento, "fuente": fuente}


# ---------------------------------------------------------------------------------------------------------------------
# Fed (USD): paginas historicas por anyo (hasta 2020) y calendario actual (2021 en adelante)
# ---------------------------------------------------------------------------------------------------------------------

def fed() -> list[dict]:
    out = []
    for y in range(DESDE, 2021):
        url = f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{y}.htm"
        for h in re.findall(r"<h5[^>]*>(.*?)</h5>", bajar(url, f"fed_{y}.html"), re.S):
            t = texto(h)
            # "March 18 Meeting", "April/May 30-1 Meeting", "March 17-18 (cancelled) Meeting": programadas (la
            # cancelada de 2020 tambien: su fecha se sabia de antemano). Conferencias, votaciones por escrito y
            # "(unscheduled)": fuera (T1).
            m = re.match(r"(.+) Meeting - (\d{4})$", t)
            if not m or "unscheduled" in m.group(1):
                continue
            cuerpo, anyo = m.groups()
            mes = [w for w in re.findall(r"[A-Za-z]+", cuerpo) if w != "cancelled"][-1].lower()
            mes = next(k for k in MESES if k.startswith(mes[:3]))
            dia = int(re.findall(r"\d+", cuerpo)[-1])  # el ultimo dia de la reunion: el del anuncio
            out.append(fila(pd.Timestamp(int(anyo), MESES[mes], dia), "USD", "Fed", url))
    url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    t = bajar(url, "fed_actual.html")
    for bloque in re.split(r"(?=<h4[^>]*>\s*<a[^>]*>\s*\d{4} FOMC Meetings)|(?=<h4[^>]*>\s*\d{4} FOMC Meetings)", t):
        y = re.search(r"(\d{4}) FOMC Meetings", bloque)
        if not y or not 2021 <= int(y.group(1)) <= HASTA:
            continue
        meses = re.findall(r'fomc-meeting__month[^"]*"><strong>([^<]+)</strong>', bloque)
        dias = re.findall(r'fomc-meeting__date[^"]*">([^<]+)</div>', bloque)
        for mes, dia in zip(meses, dias, strict=True):
            if "unscheduled" in dia.lower() or "notation" in dia.lower():
                continue
            ultimo_mes = mes.split("/")[-1].strip()
            ultimo_dia = re.findall(r"\d+", dia)[-1]
            mm = [k for k in MESES if k.startswith(ultimo_mes.lower()[:3])][0]
            out.append(fila(pd.Timestamp(int(y.group(1)), MESES[mm], int(ultimo_dia)), "USD", "Fed", url))
    return out


def empleo_eeuu() -> list[dict]:
    """Informe de empleo de EE. UU. (BLS): la fecha de publicacion va en el nombre de cada archivo (empsit_MMDDAAAA).
    La pagina bloquea programas: la lista se saco con el navegador el 14/10/2026 y se guardo en var/."""
    url = "https://www.bls.gov/bls/news-release/empsit.htm"
    fechas = (FUENTES / "bls_empsit_fechas.txt").read_text(encoding="utf-8").split()
    return [fila(pd.Timestamp(int(f[4:]), int(f[:2]), int(f[2:4])), "USD", "Empleo EE. UU.", url) for f in fechas]


def bce() -> list[dict]:
    """BCE (EUR): cada reunion de politica monetaria tiene su declaracion y rueda de prensa el dia de la decision.
    El archivo se carga por anyo (index_include); las decisiones de urgencia (p. ej. 8/10/2008) no tienen rueda de
    prensa y quedan fuera, como pide T1."""
    out = []
    for y in range(DESDE, HASTA + 1):
        url = f"https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/{y}/html/index_include.en.html"
        h = bajar(url, f"bce_{y}.html")
        for d, titulo in re.findall(r'isoDate="(\d{4}-\d{2}-\d{2})".*?class="title"><a[^>]*>(.*?)</a>', h, re.S):
            # Solo las de politica monetaria; fuera billetes, balanza de pagos, examen de los bancos (2014) y la
            # revision de estrategia (8/07/2021), que no son decisiones.
            if not re.search(r"design|banknote|balance of payments|comprehensive assessment|Opening remarks", titulo):
                out.append(fila(pd.Timestamp(d), "EUR", "BCE", url))
    return list({f["fecha"]: f for f in out}.values())  # la pagina repite fechas en los anyos recientes


def bajar_o_nada(url: str, nombre: str) -> str | None:
    """Como bajar(), pero una pagina que no existe (404) devuelve None y se recuerda como vacia."""
    f = FUENTES / nombre
    if f.exists():
        t = f.read_text(encoding="utf-8", errors="replace")
        return t or None
    try:
        return bajar(url, nombre)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        f.write_text("", encoding="utf-8")
        return None


def boe() -> list[dict]:
    """Banco de Inglaterra (GBP). Hasta 2015: actas del MPC ("held on 7 and 8 April 2004": la decision, el ultimo dia);
    fuera las "Special" (p. ej. 8/10/2008). Desde 2015: pagina de cada Monetary Policy Summary, por mes, con su fecha
    de publicacion (el dia de la decision); las especiales de 2020 tienen otra direccion y no entran (T1)."""
    out = []
    url = "https://www.bankofengland.co.uk/sitemap/minutes"
    anclas = [texto(x) for x in re.findall(r"<a[^>]*>(.*?)</a>", bajar(url, "boe_sitemap_actas.html"), re.S)]
    for titulo in anclas:
        if not re.match(r"Minutes of the (MPC|Monetary Policy Committee) Meeting (held on|ending)", titulo)                 or "pdf" in titulo:
            continue
        m = re.search(r"(?:held on|ending) (?:\d+ (?:\w+ )?and )?(\d+) (\w+) (\d{4})", titulo)
        if m and DESDE <= int(m.group(3)) <= 2015:
            d, mes, y = m.groups()
            f = pd.Timestamp(int(y), MESES[mes.lower()], int(d))
            if "ending" in titulo:  # junio y julio de 2015: la reunion acaba el miercoles y se anuncia el jueves
                f += pd.Timedelta(days=1)
            out.append(fila(f, "GBP", "BoE", url))
    for y in range(2015, HASTA + 1):
        for mes in MESES:
            for slug in (f"{mes}-{y}", f"mpc-{mes}-{y}"):  # 2015-2016 usan "mpc-noviembre-2016"
                url = f"https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/{y}/{slug}"
                h = bajar_o_nada(url, f"boe_{y}_{slug}.html")
                if h:
                    break
            if not h:
                continue
            i = h.find("Published on")
            m = re.search(r"(\d{1,2}) (\w+) (\d{4})", texto(h[i:i + 400]))
            if m:
                out.append(fila(pd.Timestamp(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1))), "GBP", "BoE",
                                url))
    return list({f["fecha"]: f for f in out}.values())


def boj() -> list[dict]:
    """Banco de Japon (JPY): tabla de actas por anyo ("Meeting on December 16 and 17"); la decision, el ultimo dia.
    Las actas salen ~6 semanas despues: las ultimas reuniones de 2026 pueden faltar (el estudio acaba en 09/2026)."""
    out = []
    for y in range(DESDE, HASTA + 1):
        url = f"https://www.boj.or.jp/en/mopo/mpmsche_minu/minu_{y}/index.htm"
        for mes, dias in re.findall(r"Meeting on (\w+) ([\d]+(?: and \d+)?)", texto(bajar(url, f"boj_{y}.html"))):
            if mes.lower() in MESES:
                out.append(fila(pd.Timestamp(y, MESES[mes.lower()], int(dias.split()[-1])), "JPY", "BoJ", url))
    # Fuera las de urgencia (T1). La tabla no las marca: avisos "Calling of an Unscheduled Monetary Policy Meeting"
    # de m_ref/index.htm (14/10/2026), mas el 18 y el 29/09/2008, una al dia siguiente de una programada y otra 12 dias
    # despues, en plena quiebra de Lehman (deducidas, no hay aviso en la lista).
    urgencia = {"2008-09-18", "2008-09-29", "2008-10-14", "2008-12-02", "2009-12-01", "2010-05-10", "2010-08-30",
                "2020-03-16", "2020-05-22"}
    # 2026: las actas de las ultimas reuniones aun no han salido; fechas del calendario oficial publicado el 31/07/2025.
    url = "https://www.boj.or.jp/en/mopo/mpmsche_minu/m_ref/mref250731a.pdf"
    for d in ("01-23", "03-19", "04-28", "06-16", "07-31", "09-18", "10-30", "12-18"):
        out.append(fila(pd.Timestamp(f"2026-{d}"), "JPY", "BoJ", url))
    return [f for f in {f["fecha"]: f for f in out}.values() if f["fecha"] not in urgencia]


FUENTES_EVENTOS = {"fed": fed, "empleo": empleo_eeuu, "bce": bce, "boe": boe, "boj": boj}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bancos", nargs="*", default=list(FUENTES_EVENTOS))
    a = ap.parse_args()
    previos = pd.read_csv(SALIDA) if SALIDA.exists() else pd.DataFrame(columns=["fecha", "divisa", "evento", "fuente"])
    nuevos = []
    for b in a.bancos:
        filas = FUENTES_EVENTOS[b]()
        evento = filas[0]["evento"] if filas else b
        previos = previos[previos["evento"] != evento]
        nuevos += filas
        anyos = pd.Series([f["fecha"][:4] for f in filas]).value_counts().sort_index()
        print(f"{b}: {len(filas)} eventos; por anyo: {dict(anyos)}")
    df = pd.concat([previos, pd.DataFrame(nuevos)]).drop_duplicates().sort_values(["fecha", "divisa", "evento"])
    df.to_csv(SALIDA, index=False)
    print(f"Total: {len(df)} filas en {SALIDA.name}")


if __name__ == "__main__":
    main()
