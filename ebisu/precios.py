"""Precios del bot en papel (docs/plan-bot-papel.md 3, 6 y 10): los cierres diarios de los 4 ETF de H1-M.

- Fuente: Yahoo (P1). La funcion que baja es inyectable: las pruebas usan una fuente inventada (sin red).
- **Un precio guardado no se cambia nunca.** Si la fuente lo revisa despues, manda el guardado y se avisa.
- Solo se guarda el cierre de un dia ya cerrado en su bolsa (B3) y con cierre de verdad (Yahoo da a veces la fila de
  hoy sin cierre). Un salto de mas del 15 % en un dia no se guarda: se avisa y se decide a mano.
- Avisos (no lanzan): salto raro, revision de la fuente, cierre ajustado distinto del cierre (B2), sin volumen 3 dias
  seguidos, pieza sin precio nuevo en 3 dias habiles.

Guardado: un CSV de solo anyadir (`fecha,pieza,cierre,ajustado,volumen,visto`).
"""

from __future__ import annotations

import csv
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

MADRID = ZoneInfo("Europe/Madrid")
# pieza -> (ISIN, simbolo en Yahoo, hora de cierre de su bolsa en Madrid)
INSTRUMENTOS = {
    "bolsa": ("IE00BK5BQT80", "VWCE.DE", time(17, 35)),
    "bonos": ("IE000K1VI152", "CEMF.DE", time(17, 35)),
    "oro": ("IE00B579F325", "SGLD.MI", time(17, 40)),
    "monetario": ("LU0290358497", "XEON.DE", time(17, 35)),
}
SALTO_MAX = 0.15
AJUSTE_MAX = 0.001
DIAS_SIN_PRECIO = 3
DIAS_SIN_VOLUMEN = 3
CAMPOS = ["fecha", "pieza", "cierre", "ajustado", "volumen", "visto"]

# Una fuente recibe (simbolo, desde) y devuelve un DataFrame indexado por fecha con Close, Adj Close y Volume.
Fuente = Callable[[str, date], pd.DataFrame]


@dataclass
class Aviso:
    tipo: str  # "salto", "revision", "ajuste", "sin_volumen", "sin_precio", "fuente"
    pieza: str
    texto: str


def yahoo(simbolo: str, desde: date) -> pd.DataFrame:
    import yfinance as yf

    d = yf.download(simbolo, start=desde.isoformat(), auto_adjust=False, progress=False)
    if d.empty:
        return pd.DataFrame(columns=["Close", "Adj Close", "Volume"])
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    return d[["Close", "Adj Close", "Volume"]]


def leer(fichero: Path) -> pd.DataFrame:
    if not fichero.exists():
        return pd.DataFrame(columns=CAMPOS)
    df = pd.read_csv(fichero, dtype={"pieza": str})
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def tabla(guardados: pd.DataFrame) -> pd.DataFrame:
    """Cierres en columnas (una por pieza), indexados por fecha."""
    if guardados.empty:
        return pd.DataFrame(columns=list(INSTRUMENTOS))
    t = guardados.pivot(index="fecha", columns="pieza", values="cierre").sort_index()
    return t.reindex(columns=list(INSTRUMENTOS))


def cerrado(dia: date, pieza: str, ahora: datetime) -> bool:
    """El dia ya ha cerrado en la bolsa de la pieza (hora de Madrid)."""
    hoy = ahora.astimezone(MADRID)
    if dia < hoy.date():
        return True
    return dia == hoy.date() and hoy.time() >= INSTRUMENTOS[pieza][2]


def nuevos_de(pieza: str, bajados: pd.DataFrame, guardados: pd.DataFrame, ahora: datetime) -> tuple[list[dict], list[Aviso]]:
    """Filas nuevas que se pueden guardar y los avisos (sin escribir nada)."""
    avisos: list[Aviso] = []
    previos = guardados[guardados["pieza"] == pieza].set_index("fecha").sort_index()
    ultimo = float(previos["cierre"].iloc[-1]) if len(previos) else None
    filas = []
    for fecha, f in bajados.sort_index().iterrows():
        dia = pd.Timestamp(fecha).normalize()
        cierre = f.get("Close")
        if pd.isna(cierre) or not cerrado(dia.date(), pieza, ahora):
            continue
        cierre, ajustado = float(cierre), float(f.get("Adj Close", cierre))
        volumen = float(f.get("Volume", 0) or 0)
        if dia in previos.index:
            antes = float(previos.loc[dia, "cierre"])
            if abs(cierre / antes - 1) > 1e-9:
                avisos.append(Aviso("revision", pieza, f"{dia:%d/%m/%Y}: la fuente dice {cierre} y se guardo {antes}"))
            continue
        if ultimo is not None and abs(cierre / ultimo - 1) > SALTO_MAX:
            avisos.append(Aviso("salto", pieza, f"{dia:%d/%m/%Y}: {ultimo} -> {cierre} (> 15 %); no se guarda"))
            break  # lo que venga despues depende de este dia: se decide a mano
        if abs(ajustado / cierre - 1) > AJUSTE_MAX:
            avisos.append(Aviso("ajuste", pieza, f"{dia:%d/%m/%Y}: cierre {cierre}, ajustado {ajustado}"))
        filas.append({"fecha": dia, "pieza": pieza, "cierre": cierre, "ajustado": ajustado, "volumen": volumen,
                      "visto": ahora.isoformat(timespec="seconds")})
        ultimo = cierre
    return filas, avisos


def vigilancia(guardados: pd.DataFrame, ahora: datetime) -> list[Aviso]:
    """Pieza sin precio nuevo en 3 dias habiles, o sin volumen 3 dias seguidos."""
    avisos = []
    hoy = pd.Timestamp(ahora.astimezone(MADRID).date())
    for pieza in INSTRUMENTOS:
        g = guardados[guardados["pieza"] == pieza].sort_values("fecha")
        if g.empty:
            avisos.append(Aviso("sin_precio", pieza, "no hay ningun precio guardado"))
            continue
        habiles = len(pd.bdate_range(g["fecha"].iloc[-1], hoy)) - 1
        if habiles >= DIAS_SIN_PRECIO:
            avisos.append(Aviso("sin_precio", pieza, f"ultimo precio del {g['fecha'].iloc[-1]:%d/%m/%Y} "
                                                     f"({habiles} dias habiles)"))
        if len(g) >= DIAS_SIN_VOLUMEN and (g["volumen"].tail(DIAS_SIN_VOLUMEN) <= 0).all():
            avisos.append(Aviso("sin_volumen", pieza, f"sin volumen los ultimos {DIAS_SIN_VOLUMEN} dias"))
    return avisos


def actualizar(fichero: Path, ahora: datetime, fuente: Fuente = yahoo,
               desde: date = date(2019, 1, 1)) -> tuple[pd.DataFrame, list[Aviso]]:
    """Baja, valida y anyade al CSV lo nuevo. Devuelve la tabla de cierres y los avisos. Nunca reescribe lo guardado."""
    guardados = leer(fichero)
    avisos: list[Aviso] = []
    nuevas: list[dict] = []
    for pieza, (_, simbolo, _) in INSTRUMENTOS.items():
        try:
            bajados = fuente(simbolo, desde)
        except Exception as exc:  # una fuente caida no tumba el dia: se avisa
            avisos.append(Aviso("fuente", pieza, f"{simbolo}: {type(exc).__name__}"))
            continue
        filas, av = nuevos_de(pieza, bajados, guardados, ahora)
        nuevas += filas
        avisos += av
    if nuevas:
        fichero.parent.mkdir(parents=True, exist_ok=True)
        existe = fichero.exists()
        with fichero.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS)
            if not existe:
                w.writeheader()
            for fila in nuevas:
                w.writerow({**fila, "fecha": fila["fecha"].date().isoformat()})
        guardados = leer(fichero)
    avisos += vigilancia(guardados, ahora)
    return tabla(guardados), avisos
