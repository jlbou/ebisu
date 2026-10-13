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


def snb() -> list[dict]:
    """Banco Nacional Suizo (CHF): evaluaciones trimestrales ("Monetary policy assessment of 13 September 2007").
    Las decisiones fuera de calendario (p. ej. el suelo de 6/09/2011 o su fin el 15/01/2015) tienen otro titulo y no
    entran (T1)."""
    url = "https://www.snb.ch/en/the-snb/mandates-goals/monetary-policy/decisions"
    out = []
    h = bajar(url, "snb_decisiones.html")
    for d, mes, y in re.findall(r"assessment of (\d{1,2}) (\w+) (\d{4})", texto(h)):
        if mes.lower() in MESES and DESDE <= int(y) <= HASTA:
            out.append(fila(pd.Timestamp(int(y), MESES[mes.lower()], int(d)), "CHF", "SNB", url))
    # Hasta 2006 el titulo no lleva la fecha: se toma la del enlace (pre_AAAAMMDD) de cada "Monetary policy assessment"
    for f, titulo in re.findall(r"<a[^>]*pre_(\d{8})[^>]*>(.*?)</a>", h, re.S):
        if texto(titulo).startswith("Monetary policy assessment") and DESDE <= int(f[:4]) <= HASTA:
            out.append(fila(pd.Timestamp(f), "CHF", "SNB", url))
    return list({f["fecha"]: f for f in out}.values())


def rbnz() -> list[dict]:
    """Banco de Nueva Zelanda (NZD): cronologia oficial de anuncios del OCR. La web bloquea programas: la tabla se
    copio con el navegador el 14/10/2026 a var/. Fuera las de urgencia de 2020 (16/03, 23/03 y 7/04; T1)."""
    url = "https://www.rbnz.govt.nz/monetary-policy/monetary-policy-decisions"
    urgencia = {"2020-03-16", "2020-03-23", "2020-04-07"}
    out = []
    for s in (FUENTES / "rbnz_decisiones.txt").read_text(encoding="utf-8").strip().split("|"):
        d, mes, y = s.split()
        f = pd.Timestamp(int(y), MESES[mes.lower()], int(d))
        if f.date().isoformat() not in urgencia:
            out.append(fila(f, "NZD", "RBNZ", url))
    return out


def rba() -> list[dict]:
    """Banco de la Reserva de Australia (AUD). Desde 12/2007: un comunicado tras cada reunion (paginas anuales de
    decisiones, copiadas con el navegador el 14/10/2026: la web bloquea programas). Antes solo habia comunicado si
    cambiaba el tipo, asi que 2003-11/2007 se deduce de la regla de entonces: reunion el primer martes de cada mes salvo
    enero y anuncio el miercoles por la manyana; comprobada con los 11 cambios de 2003-2007 (todos caen en ese
    miercoles). Fuera la de urgencia del 19/03/2020 (T1)."""
    url = "https://www.rba.gov.au/monetary-policy/int-rate-decisions/"
    out = []
    for y in range(DESDE, 2008):
        for mes in range(2, 13):
            if (y, mes) == (2007, 12):
                continue
            primer_martes = pd.Timestamp(y, mes, 1) + pd.Timedelta(days=(1 - pd.Timestamp(y, mes, 1).weekday()) % 7)
            out.append(fila(primer_martes + pd.Timedelta(days=1), "AUD", "RBA", url + "(regla)"))
    out.append(fila(pd.Timestamp("2007-12-05"), "AUD", "RBA", url + "2007/"))
    for s in (FUENTES / "rba_decisiones_2008_2026.txt").read_text(encoding="utf-8").strip().split("|"):
        d, mes, y = s.split()
        f = pd.Timestamp(int(y), MESES[mes.lower()], int(d))
        if f.date().isoformat() != "2020-03-19":
            out.append(fila(f, "AUD", "RBA", url + y + "/"))
    return out


BOC_CALENDARIOS = {  # comunicado de cada verano con las fechas del anyo siguiente (archivo mensual de la web)
    2003: "2002/08/bank-canada-releases-2003-schedule", 2004: "2003/07/bank-canada-releases-2004-schedule",
    2005: "2004/07/bank-canada-releases-2005-schedule", 2006: "2005/08/bank-canada-releases-2006-schedule-dates",
    2007: "2006/07/bank-canada-releases-2007-schedule", 2008: "2007/07/bank-canada-releases-2008-schedule-dates",
    2009: "2008/07/bank-canada-releases-2009-schedule", 2010: "2009/07/bank-canada-releases-2010-schedule-dates",
    2011: "2010/07/bank-canada-releases-2011-schedule-dates", 2012: "2011/07/bank-canada-2012-schedule-fad-mpr",
    2013: "2012/08/2013-schedule-policy-interest-rate-announcements-monetary-policy-report",
    2014: "2013/07/bofc-publishes-2014-schedule-fad-and-mpr-releases",
    2015: "2014/07/boc-2015-schedule-fad-mpr-releases", 2016: "2015/07/boc-2016-schedule-fad-mpr-releases",
    2017: "2016/07/boc-2017-schedule-fad-mpr-releases", 2018: "2017/07/boc-2018-schedule-fad-mpr-releases",
    2019: "2018/07/bank-canada-publishes-2019-schedule-fad-announcements-release-mpr-bos-slos",
    2020: "2019/07/bank-canada-publishes-2020-schedule-policy-interest-rate-announcements-release-mpr-other-major-"
          "publications",
    2021: "2020/07/2021-schedule-policy-interest-rate-announcements",
    2022: "2021/07/bank-canada-publishes-its-2022-schedule-policy-interest-rate-announcements-release-monetary-"
          "policy-report-other-major-publications",
    2023: "2022/07/2023-schedule-interest-rate-announcements",
    2024: "2023/07/2024-schedule-policy-interest-rate-announcements-major-publications",
    2025: "2024/08/bank-canada-publishes-2025-schedule-policy-interest-rate-announcements-other-major-publications",
    2026: "2025/08/bank-canada-publishes-2026-schedule-policy-interest-rate-announcements-other-major-publications",
}


def boc() -> list[dict]:
    """Banco de Canada (CAD): fechas fijas de anuncio publicadas cada verano para el anyo siguiente. Al ser el
    calendario anunciado, las decisiones de urgencia (8/10/2008, 13 y 27/03/2020) no entran (T1).

    El texto da fechas con o sin anyo ("Tuesday 21 January 2003", "Wednesday, January 9"); las que no lo llevan toman
    el ultimo anyo mencionado antes ("...for 2019 are as follows: ..."). Solo cuenta la parte de los anuncios de tipos
    (hasta "All ... announcements will"), no la de otras publicaciones."""
    out = []
    mes_re = "|".join(m.capitalize() for m in MESES)
    patron = re.compile(rf"(?P<dmy>\b\d{{1,2}} (?:{mes_re}),? \d{{4}}\b)|(?P<mdy>\b(?:{mes_re}) \d{{1,2}},? \d{{4}}\b)"
                        rf"|(?P<dm>\b\d{{1,2}} (?:{mes_re})\b)|(?P<md>\b(?:{mes_re}) \d{{1,2}}\b)|(?P<y>\b20\d{{2}}\b)")
    for y, ruta in BOC_CALENDARIOS.items():
        url = f"https://www.bankofcanada.ca/{ruta}/"
        h = re.sub(r"<style.*?</style>|<script.*?</script>", "", bajar(url, f"boc_calendario_{y}.html"), flags=re.S)
        cuerpo = texto(h)
        cuerpo = cuerpo[cuerpo.find("Media Relations"):]
        fin = re.search(r"All (?:interest )?(?:rate )?announcements will|The Monetary Policy Report will|"
                        r"The scheduled dates for the release", cuerpo)
        cuerpo = cuerpo[:fin.start()] if fin else cuerpo
        anyo = None
        for m in patron.finditer(cuerpo):
            s = m.group(0).replace(",", "")
            if m.lastgroup == "y":
                anyo = int(s)
                continue
            partes = s.split()
            if m.lastgroup in ("dmy", "mdy"):
                anyo_f = int(partes[-1])
                partes = partes[:-1]
                anyo = anyo_f
            else:
                anyo_f = anyo
            d, mes = (partes[0], partes[1]) if partes[0].isdigit() else (partes[1], partes[0])
            if anyo_f == y:
                out.append(fila(pd.Timestamp(y, MESES[mes.lower()], int(d)), "CAD", "BoC", url))
    return list({f["fecha"]: f for f in out}.values())


FUENTES_EVENTOS = {"fed": fed, "empleo": empleo_eeuu, "bce": bce, "boe": boe, "boj": boj, "snb": snb, "rbnz": rbnz,
                   "rba": rba, "boc": boc}


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
