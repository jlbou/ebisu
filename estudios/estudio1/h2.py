"""H2: rango del dia anterior en divisas (docs/diseno-estudio-1.md, seccion 3, H2). Montaje de los dias y simulacion.

Dias: las velas de 1 hora de Dukascopy (compra y venta) se agrupan en dias de 17:00 a 17:00 de Nueva York (la hora de
Nueva York con su horario de verano); las horas sin volumen (fin de semana) no cuentan.

Regla, por par y dia (sin apalancamiento, una operacion como mucho por dia y par, cerrada el mismo dia):
- Se compra si el precio de VENTA del mercado (ask) baja hasta el minimo de ayer de ese mismo precio, a ese nivel.
- Se vende al maximo de ayer del precio de COMPRA del mercado (bid) si se toca ese dia; si no, al cierre (bid).
- Con velas diarias no se sabe que se toco antes: si el mismo dia se tocan los dos niveles, se cuenta lo peor
  (vender al menor entre el maximo de ayer y el cierre).
- El diferencial sale de usar ask para comprar y bid para vender: no se suma ningun coste supuesto.

Cartera: el capital se reparte a partes iguales entre los 7 pares; lo que no esta en una operacion rinde como el
monetario (como en H1). Impuestos: cada operacion es una ganancia o perdida; neto anual al 19 %, perdidas arrastradas
4 anyos (la regla de los dos meses es de valores, no de divisas). Se paga el ultimo dia habil del anyo.

Uso: .venv/Scripts/python.exe estudios/estudio1/h2.py --validar   (datos inventados; no mide nada)
"""

from __future__ import annotations

import argparse
import lzma
import struct
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DUKAS = RAIZ / "var" / "estudio1" / "dukascopy"
PARES = ["EURUSD", "USDJPY", "GBPUSD", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
TIPO = 0.19


def leer_mes(fichero: Path, divisor: float, inicio_mes: pd.Timestamp) -> pd.DataFrame:
    datos = fichero.read_bytes()
    if not datos:
        return pd.DataFrame()
    raw = lzma.decompress(datos)
    filas = [struct.unpack(">5If", raw[i:i + 24]) for i in range(0, len(raw), 24)]
    df = pd.DataFrame(filas, columns=["s", "o", "c", "l", "h", "vol"])
    df = df[df["vol"] > 0]
    df.index = inicio_mes + pd.to_timedelta(df["s"], unit="s")
    return df[["o", "h", "l", "c"]] / divisor


def dias_de_par(par: str) -> pd.DataFrame:
    """Velas diarias de 17:00 a 17:00 de Nueva York: columnas bid_o..bid_c y ask_o..ask_c.

    Solo cuentan las horas que tienen precio de compra Y de venta (si no, en el cambio de mes el cierre de un lado y
    el del otro podian ser de horas distintas)."""
    divisor = 1e3 if par.endswith("JPY") else 1e5
    bid = {f.name[:7] for f in (DUKAS / par).glob("*_BID.bi5")}
    ask = {f.name[:7] for f in (DUKAS / par).glob("*_ASK.bi5")}
    if bid != ask:
        faltan = sorted(bid ^ ask)
        raise ValueError(f"{par}: faltan ficheros de un lado en {len(faltan)} meses (p. ej. {faltan[:3]}): "
                         "termina la bajada antes de montar los dias")
    horas = {}
    for lado in ("BID", "ASK"):
        trozos = []
        for f in sorted((DUKAS / par).glob(f"*_{lado}.bi5")):
            anyo, mes = int(f.name[:4]), int(f.name[5:7])
            trozos.append(leer_mes(f, divisor, pd.Timestamp(year=anyo, month=mes, day=1, tz="UTC")))
        horas[lado.lower()] = pd.concat([x for x in trozos if len(x)]).sort_index()
    h = horas["bid"].add_prefix("bid_").join(horas["ask"].add_prefix("ask_"), how="inner")
    dia = (h.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)).date  # 17:00 NY -> 00:00 del dia siguiente
    g = h.groupby(dia)
    d = pd.DataFrame({f"{s}_{k}": getattr(g[f"{s}_{c}"], fn)() for s in ("bid", "ask")
                      for k, c, fn in (("o", "o", "first"), ("h", "h", "max"), ("l", "l", "min"), ("c", "c", "last"))})
    d.index = pd.DatetimeIndex(d.index)
    return d


def operaciones(d: pd.DataFrame) -> pd.Series:
    """Rendimiento de cada operacion (indexado por el dia en que se hace)."""
    ayer = d.shift(1)
    entra = d["ask_l"] <= ayer["ask_l"]
    toca_max = d["bid_h"] >= ayer["bid_h"]
    entrada = ayer["ask_l"]
    # Solo se toca el minimo: se vende al cierre. Se tocan los dos: lo peor (no se sabe el orden).
    salida = np.where(toca_max, np.minimum(ayer["bid_h"], d["bid_c"]), d["bid_c"])
    r = pd.Series(salida / entrada - 1, index=d.index)
    return r[entra & ayer["ask_l"].notna()]


@dataclass
class ResultadoH2:
    valor: pd.Series
    bolsillo: float
    impuestos: float
    por_operacion: dict


def simular_h2(dias: dict[str, pd.DataFrame], monetario: pd.Series, inicio: str, fin: str) -> ResultadoH2:
    ops = {p: operaciones(d).loc[inicio:fin] for p, d in dias.items()}
    fechas = monetario.loc[inicio:fin].index
    r_mon = monetario.reindex(fechas).pct_change().fillna(0)
    n = len(dias)
    valor, v, neto, pagado, arrastre, serie = 1.0, 1.0, 0.0, 0.0, deque(), []

    def impuesto_anyo(anyo: int) -> float:
        nonlocal neto
        base = neto
        while arrastre and arrastre[0][0] < anyo - 4:
            arrastre.popleft()
        while base > 0 and arrastre:
            a0, perd = arrastre.popleft()
            usar = min(base, -perd)
            base -= usar
            if -perd > usar:
                arrastre.appendleft((a0, perd + usar))
        if base < 0:
            arrastre.append((anyo, base))
            base = 0.0
        neto = 0.0
        return TIPO * base

    for k, d in enumerate(fechas):
        hoy = [ops[p].get(d) for p in ops]
        ganancia = sum(v / n * r for r in hoy if r is not None and not np.isnan(r))
        neto += ganancia
        v = v * (1 + r_mon.iloc[k]) + ganancia
        if k + 1 < len(fechas) and fechas[k + 1].year != d.year:
            imp = impuesto_anyo(d.year)
            pagado += imp
            v -= imp
        serie.append(v)
    imp = impuesto_anyo(fechas[-1].year)
    pagado += imp
    return ResultadoH2(pd.Series(serie, index=fechas), serie[-1] - imp, pagado, {p: o.to_numpy() for p, o in ops.items()})


# ---------------------------------------------------------------------------------------------------------------------
FALLOS: list[str] = []


def comprobar(nombre: str, obtenido: float, esperado: float, tol: float = 1e-12) -> None:
    ok = abs(obtenido - esperado) <= tol
    print(f"{'OK   ' if ok else 'FALLA'} {nombre}: obtenido {obtenido:.10f}, esperado {esperado:.10f}")
    if not ok:
        FALLOS.append(nombre)


def dia(bo, bh, bl, bc, sp=0.0002):
    return {"bid_o": bo, "bid_h": bh, "bid_l": bl, "bid_c": bc,
            "ask_o": bo + sp, "ask_h": bh + sp, "ask_l": bl + sp, "ask_c": bc + sp}


def validar() -> None:
    f = pd.bdate_range("2003-01-06", periods=5)
    d = pd.DataFrame([
        dia(1.10, 1.12, 1.09, 1.11),  # 0: referencia
        dia(1.11, 1.115, 1.095, 1.10),  # 1: no baja del minimo de ayer (1,09) -> no opera
        dia(1.10, 1.13, 1.09, 1.12),  # 2: toca minimo (1,095) y maximo (1,115): lo peor -> min(1,115, 1,12)
        dia(1.11, 1.12, 1.08, 1.085),  # 3: toca minimo (1,09) y no el maximo (1,13) -> cierre 1,085
        dia(1.09, 1.11, 1.07, 1.10),  # 4: toca minimo (1,08) y maximo (1,12)? no (1,11 < 1,12) -> cierre 1,10
    ], index=f)
    r = operaciones(d)
    comprobar("dias con operacion", len(r), 3)
    comprobar("dia 2: los dos niveles, lo peor", r[f[2]], 1.115 / 1.0952 - 1)
    comprobar("dia 3: solo el minimo, al cierre", r[f[3]], 1.085 / 1.0902 - 1)
    comprobar("dia 4: solo el minimo, al cierre", r[f[4]], 1.10 / 1.0802 - 1)
    # El diferencial cuesta: con diferencial 0 el mismo dia 3 rinde mas.
    d0 = pd.DataFrame([dia(*[d.iloc[i][c] for c in ("bid_o", "bid_h", "bid_l", "bid_c")], sp=0.0) for i in range(5)], index=f)
    comprobar("el diferencial resta", float(operaciones(d0)[f[3]] > r[f[3]]), 1.0)

    # Cartera: precios que suben un poco cada dia (nunca bajan del minimo de ayer) salvo dos dias, uno en 2003 y otro
    # en 2004: una operacion por anyo y par. Monetario plano. A mano: 2003 paga sobre su ganancia; 2004 compensa.
    f2 = pd.bdate_range("2003-01-01", "2004-12-31")
    lo = 1.0 + 0.0001 * np.arange(len(f2))
    base = pd.DataFrame([dia(x, x + 0.01, x, x + 0.005, 0.0002) for x in lo], index=f2)
    i1, i2 = 10, 300
    base.iloc[i1] = pd.Series(dia(lo[i1], lo[i1] + 0.003, lo[i1 - 1] - 0.002, lo[i1 - 1] + 0.004, 0.0002))
    base.iloc[i2] = pd.Series(dia(lo[i2], lo[i2] + 0.003, lo[i2 - 1] - 0.004, lo[i2 - 1] - 0.003, 0.0002))
    ops = operaciones(base)
    comprobar("cartera: una operacion por anyo", len(ops), 2)
    r1 = (lo[i1 - 1] + 0.004) / (lo[i1 - 1] + 0.0002) - 1  # gana (cierre por encima de la entrada)
    r2 = (lo[i2 - 1] - 0.003) / (lo[i2 - 1] + 0.0002) - 1  # pierde
    comprobar("cartera: operacion de 2003", float(ops.iloc[0]), r1)
    comprobar("cartera: operacion de 2004", float(ops.iloc[1]), r2)
    res = simular_h2({p: base for p in PARES}, pd.Series(1.0, index=f2), "2003-01-01", "2004-12-31")
    imp_2003 = TIPO * r1  # los 7 pares a 1/7 cada uno: la cartera gana r1
    v_2004 = (1 + r1 - imp_2003)
    perdida_2004 = v_2004 * r2
    comprobar("cartera: impuestos (solo 2003; la perdida de 2004 se arrastra)", res.impuestos, imp_2003)
    comprobar("cartera: bolsillo", res.bolsillo, v_2004 + perdida_2004)

    print()
    print("VALIDACION DE H2:", "TODO OK" if not FALLOS else f"FALLAN {len(FALLOS)}: {', '.join(FALLOS)}")
    sys.exit(1 if FALLOS else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validar", action="store_true")
    if ap.parse_args().validar:
        validar()
    else:
        sys.exit("Solo --validar por ahora: la medicion se hace con el juez, con las 5 variantes juntas.")
