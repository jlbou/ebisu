"""Monta las piezas del estudio 4 en euros (docs/plan-estudio-4.md 3 y 13) y hace las comprobaciones antes de medir.

Piezas (indices diarios, base 1 el primer dia, 01/07/1969 - 30/09/2026; NO se ensenya ningun rendimiento):
- bolsa: EE. UU. con dividendos (Kenneth French, Mkt-RF + RF) hasta 1996; desde 1997, 60 % EE. UU. + 40 % MSCI EAFE
  (con dividendos desde 2001; en 1997-2000, precio + la diferencia mensual con Kenneth French International Indices,
  repartida por dias), rebalanceado el primer dia habil de cada mes; sin cubrir.
- bonos: bono de EE. UU. a 7 anyos (FRED DGS7) revalorizado cada dia como un bono a la par (cupon semestral = la
  rentabilidad del dia anterior) + devengo; cubierto a euros con (tipo del euro - DTB3) por dias / 360.
- oro: fixing de Frankfurt (Bundesbank) hasta 1998; 01/1999-08/2000, medias mensuales (DataHub, World Gold Council /
  Banco Mundial) a mitad de mes, interpolacion lineal; desde el 30/08/2000, GC=F como en el estudio 1. En euros por onza.
- monetario: tipo aleman a un dia (FRED IRSTCI01DEM156N, mensual) hasta 1998; EONIA y STR (BCE) despues.
Cambio: marco/dolar del Bundesbank hasta 1998 (1,95583 marcos por euro); BCE despues.

Comprobaciones (solo correlaciones de rendimientos mensuales, >= 0,95) y calidad de datos (huecos, saltos).

Uso: .venv/Scripts/python.exe estudios/estudio4/montar.py
Salida: var/estudio4/piezas_eur.csv (y bolsa_usd para la capa 6).
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
F = RAIZ / "var" / "estudio4" / "fuentes"
E1 = RAIZ / "var" / "estudio1"
INV = RAIZ / "var" / "inventario"
SALIDA = RAIZ / "var" / "estudio4" / "piezas_eur.csv"
INICIO, FIN = pd.Timestamp("1969-07-01"), pd.Timestamp("2026-09-30")
MUNDIAL, EAFE_DIV, EURO = pd.Timestamp("1997-01-01"), pd.Timestamp("2001-01-01"), pd.Timestamp("1999-01-01")
GC_DESDE, CAMBIO_STR = pd.Timestamp("2000-08-30"), pd.Timestamp("2019-10-01")
DEM_EUR, ONZAS_KG, UMBRAL = 1.95583, 32.1507466, 0.95


# --- lectura de fuentes -------------------------------------------------------------------------------------------

def fred(s: str) -> pd.Series:
    df = pd.read_csv(F / f"fred_{s}.csv", index_col=0, parse_dates=True, na_values=".")
    return df.iloc[:, 0].astype(float).dropna()


def bundesbank(nombre: str) -> pd.Series:
    filas = [ln.split(",") for ln in (F / f"{nombre}.csv").read_text(encoding="utf-8-sig").splitlines()]
    datos = [(f[0], f[1]) for f in filas if re.fullmatch(r"\d{4}-\d{2}-\d{2}", f[0]) and f[1] not in ("", ".")]
    return pd.Series([float(v) for _, v in datos], index=pd.to_datetime([d for d, _ in datos]))


def french_diario() -> pd.Series:
    df = pd.read_csv(F / "french_diario" / "F-F_Research_Data_Factors_daily.csv", skiprows=4, index_col=0)
    df = df[df.index.astype(str).str.fullmatch(r"\d{8}")]
    total = (df["Mkt-RF"].astype(float) + df["RF"].astype(float)) / 100
    return pd.Series(total.to_numpy(), index=pd.to_datetime(df.index.astype(str)))


def french_internacional() -> pd.Series:
    """Rendimiento mensual (dolares, con dividendos) de 'Ind_all', primer bloque (ponderado por valor), columna Mkt."""
    filas = {}
    for ln in (F / "french_internacional" / "Ind_all.Dat").read_text().splitlines():
        m = re.match(r"^\s*(\d{6})\s+(-?\d+\.\d+)", ln)
        if m and m.group(1) not in filas:
            filas[m.group(1)] = float(m.group(2)) / 100
        elif filas and not m and ln.strip() and not ln.strip()[0].isdigit() and len(filas) > 12 and "Weight" in ln:
            break
    return pd.Series(filas.values(), index=pd.to_datetime(list(filas.keys()), format="%Y%m") + pd.offsets.MonthEnd(0))


def msci(nombre: str) -> pd.Series:
    df = pd.read_csv(F / f"{nombre}.csv")
    return pd.Series(df["nivel"].astype(float).to_numpy(), index=pd.to_datetime(df["fecha"].astype(str)))


def bce(nombre: str) -> pd.Series:
    df = pd.read_csv(E1 / f"bce_{nombre}.csv", index_col=0, parse_dates=True)
    return df["valor"].astype(float).dropna()


def yahoo(nombre: str, col: str = "Adj Close") -> pd.Series:
    df = pd.read_csv(INV / f"{nombre}.csv", index_col=0, parse_dates=True)
    return df[col].astype(float).dropna()


# --- piezas -------------------------------------------------------------------------------------------------------

def en(serie: pd.Series, fechas: pd.DatetimeIndex) -> pd.Series:
    """Valor vigente en cada fecha (el ultimo conocido)."""
    return serie.reindex(serie.index.union(fechas)).sort_index().ffill().reindex(fechas)


def usd_por_eur(fechas: pd.DatetimeIndex) -> pd.Series:
    antes = DEM_EUR / bundesbank("bbk_dem_usd")
    serie = pd.concat([antes[antes.index < EURO], bce("eurusd")[bce("eurusd").index >= EURO]])
    return en(serie, fechas)


def devengo(tipo_pct: pd.Series, fechas: pd.DatetimeIndex) -> pd.Series:
    """Factor diario 1 + tipo * dias naturales / 360, con el tipo vigente el dia anterior."""
    t = en(tipo_pct, fechas)
    dias = fechas.to_series().diff().dt.days.fillna(0).to_numpy()
    return pd.Series(1 + t.shift(1).fillna(0).to_numpy() / 100 * dias / 360, index=fechas)


def tipo_euro() -> pd.Series:
    aleman = fred("IRSTCI01DEM156N")
    eonia, estr = bce("eonia"), bce("estr")
    return pd.concat([aleman[aleman.index < EURO], eonia[(eonia.index >= EURO) & (eonia.index < CAMBIO_STR)],
                      estr[estr.index >= CAMBIO_STR]])


def precio_par(y_nueva: np.ndarray, cupon: np.ndarray, anyos: int = 7) -> np.ndarray:
    """Precio (por 1) de un bono con cupon semestral 'cupon' y 'anyos' de vida, valorado a la rentabilidad 'y_nueva'."""
    k = np.arange(1, 2 * anyos + 1)
    desc = (1 + y_nueva[:, None] / 2) ** (-k[None, :])
    return (cupon[:, None] / 2 * desc).sum(axis=1) + desc[:, -1]


def rendimiento_bono(y_pct: pd.Series, fechas: pd.DatetimeIndex) -> pd.Series:
    y = en(y_pct, fechas).to_numpy() / 100
    y0 = np.r_[y[0], y[:-1]]
    dias = fechas.to_series().diff().dt.days.fillna(0).to_numpy()
    r = precio_par(y, y0) - 1 + y0 * dias / 365
    r[0] = 0.0
    return pd.Series(r, index=fechas)


def bolsa_usd(fechas: pd.DatetimeIndex) -> pd.Series:
    r_us = french_diario().reindex(fechas).fillna(0)  # festivo en EE. UU.: el precio no cambia
    us = (1 + r_us).cumprod()
    # EAFE: con dividendos desde 2001; antes, precio + diferencia mensual con Kenneth French repartida por dias.
    precio, con_div = msci("msci_eafe_precio"), msci("msci_eafe_con_div")
    r_precio = en(precio, fechas).pct_change()
    r_div = en(con_div, fechas).pct_change()
    mens_precio = precio.resample("ME").last().pct_change()
    extra = (french_internacional() - mens_precio).dropna()  # dividendos del mes (aprox.)
    por_mes = fechas.to_series().groupby(fechas.to_period("M")).transform("count")
    extra_d = (1 + extra.reindex(fechas.to_period("M").to_timestamp("M")).to_numpy()) ** (1 / por_mes.to_numpy()) - 1
    r_eafe = np.where(fechas >= EAFE_DIV, r_div.to_numpy(), r_precio.to_numpy() + np.nan_to_num(extra_d))
    r_eafe = pd.Series(r_eafe, index=fechas).fillna(0)
    eafe = (1 + r_eafe).cumprod()
    # Mezcla 60/40 desde 1997, con rebalanceo el primer dia habil de cada mes; antes, solo EE. UU.
    valor, n_us, n_in, mes, out = None, 0.0, 0.0, None, []
    for d, pu, pi in zip(fechas, us.to_numpy(), eafe.to_numpy(), strict=True):
        if d < MUNDIAL:
            out.append(pu)
            continue
        if valor is None:
            valor = out[-1] if out else pu
        if d.month != mes:
            if mes is not None:
                valor = n_us * pu + n_in * pi
            n_us, n_in, mes = 0.6 * valor / pu, 0.4 * valor / pi, d.month
        out.append(n_us * pu + n_in * pi)
    return pd.Series(out, index=fechas), r_eafe


def oro_eur(fechas: pd.DatetimeIndex, fx: pd.Series) -> pd.Series:
    fr = bundesbank("bbk_oro_frankfurt") / DEM_EUR / ONZAS_KG  # euros por onza
    fr = fr[fr.index < EURO]
    dh = pd.read_csv(F / "datahub_oro_mensual.csv")
    dh = pd.Series(dh["Price"].astype(float).to_numpy(), index=pd.to_datetime(dh["Date"]) + pd.Timedelta(days=14))
    fx_mes = fx.groupby(fx.index.to_period("M")).mean()
    dh = dh[(dh.index >= EURO) & (dh.index < GC_DESDE)]
    dh = dh / fx_mes.reindex(dh.index.to_period("M")).to_numpy()
    gc = yahoo("GC_F", "Close")
    gc = gc[gc.index >= GC_DESDE] / en(fx, gc.index[gc.index >= GC_DESDE]).reindex(gc.index[gc.index >= GC_DESDE])
    puntos = pd.concat([fr, dh, gc]).sort_index()
    hueco = (fechas >= EURO) & (fechas < GC_DESDE)
    interp = puntos.reindex(puntos.index.union(fechas)).sort_index().interpolate("time").reindex(fechas)
    return pd.Series(np.where(hueco, interp, en(puntos, fechas)), index=fechas)


def montar() -> pd.DataFrame:
    dias_us = french_diario().index
    dias_fx = bundesbank("bbk_dem_usd").index.union(bce("eurusd").index)
    fechas = dias_us.union(dias_fx)
    fechas = fechas[(fechas >= INICIO) & (fechas <= FIN) & (fechas.dayofweek < 5)]
    fx = usd_por_eur(fechas)
    b_usd, _ = bolsa_usd(fechas)
    bolsa = b_usd / fx
    r_bono = rendimiento_bono(fred("DGS7"), fechas)
    eur = tipo_euro()
    bonos = (1 + r_bono + devengo(eur, fechas) - devengo(fred("DTB3"), fechas)).cumprod()
    oro = oro_eur(fechas, fx)
    monetario = devengo(eur, fechas).cumprod()
    piezas = pd.DataFrame({"bolsa": bolsa, "bonos": bonos, "oro": oro, "monetario": monetario, "bolsa_usd": b_usd,
                           "bono_usd": (1 + r_bono).cumprod()})
    return piezas / piezas.iloc[0]


# --- comprobaciones -----------------------------------------------------------------------------------------------

def corr_mensual(a: pd.Series, b: pd.Series) -> tuple[float, int, str]:
    a, b = a.dropna(), b.dropna()
    comun = a.index.intersection(b.index)
    ma = a.reindex(comun).resample("ME").last().pct_change()
    mb = b.reindex(comun).resample("ME").last().pct_change()
    ok = ma.notna() & mb.notna()
    return float(ma[ok].corr(mb[ok])), int(ok.sum()), f"{comun.min():%Y-%m}"


def comprobaciones(p: pd.DataFrame) -> list[tuple]:
    e1 = pd.read_csv(E1 / "piezas_eur.csv", index_col=0, parse_dates=True)
    filas = [
        ("bolsa", "estudio 1 (VTSMX/VGTSX)", *corr_mensual(p["bolsa"], e1["bolsa"])),
        ("bolsa", "EUNL.DE", *corr_mensual(p["bolsa"], yahoo("EUNL.DE", "Close"))),
        ("bolsa", "VWCE.DE", *corr_mensual(p["bolsa"], yahoo("VWCE.DE", "Close"))),
        ("bolsa EE. UU. (USD, hasta 1996)", "VTSMX", *corr_mensual(p["bolsa_usd"][p.index < MUNDIAL], yahoo("VTSMX"))),
        ("bolsa (USD)", "VT", *corr_mensual(p["bolsa_usd"], yahoo("VT"))),
        ("bonos", "estudio 1 (VBMFX cubierto)", *corr_mensual(p["bonos"], e1["bonos"])),
        ("bonos", "EUNA.DE", *corr_mensual(p["bonos"], yahoo("EUNA.DE", "Close"))),
        ("bono a 7 anyos (USD)", "VBMFX", *corr_mensual(p["bono_usd"], yahoo("VBMFX"))),
        ("oro", "4GLD.DE", *corr_mensual(p["oro"], yahoo("4GLD.DE", "Close"))),
        ("monetario", "XEON.DE", *corr_mensual(p["monetario"], yahoo("XEON.DE", "Close"))),
    ]
    # Oro de Frankfurt frente a la media mensual de DataHub (las dos como medias del mes, en dolares), 1969-1998.
    fr = bundesbank("bbk_oro_frankfurt") / ONZAS_KG / en(bundesbank("bbk_dem_usd"), bundesbank("bbk_oro_frankfurt").index)
    fr_m = fr[(fr.index >= INICIO) & (fr.index < EURO)].resample("ME").mean().pct_change()
    dh = pd.read_csv(F / "datahub_oro_mensual.csv")
    dh = pd.Series(dh["Price"].astype(float).to_numpy(), index=pd.to_datetime(dh["Date"]) + pd.offsets.MonthEnd(0))
    dh_m = dh.pct_change().reindex(fr_m.index)
    ok = fr_m.notna() & dh_m.notna()
    filas.append(("oro Frankfurt (medias, USD)", "DataHub mensual", float(fr_m[ok].corr(dh_m[ok])), int(ok.sum()),
                  f"{fr_m[ok].index.min():%Y-%m}"))
    # Tipo aleman frente al EONIA (niveles mensuales, 1999-2021).
    al, eo = fred("IRSTCI01DEM156N"), bce("eonia").resample("MS").mean()
    comun = al.index.intersection(eo.index)
    filas.append(("tipo aleman (nivel)", "EONIA", float(al[comun].corr(eo[comun])), len(comun), f"{comun.min():%Y-%m}"))
    # EAFE reconstruido frente a Kenneth French (mensual, 2001-2025) para comprobar que 'Ind_all' es lo mismo.
    con_div = msci("msci_eafe_con_div").resample("ME").last().pct_change()
    fi = french_internacional().reindex(con_div.index)
    ok = con_div.notna() & fi.notna()
    filas.append(("Kenneth French Ind_all", "MSCI EAFE con div.", float(con_div[ok].corr(fi[ok])), int(ok.sum()),
                  f"{con_div[ok].index.min():%Y-%m}"))
    return filas


def calidad(p: pd.DataFrame) -> None:
    print(f"\nCalidad: {p.index.min().date()} a {p.index.max().date()}, {len(p)} dias, duplicados "
          f"{int(p.index.duplicated().sum())}, huecos (NaN) {int(p.isna().sum().sum())}")
    saltos = p.index.to_series().diff().dt.days
    print(f"Saltos de calendario > 4 dias: {int((saltos > 4).sum())}")
    for col in ["bolsa", "bonos", "oro", "monetario"]:
        r = p[col].pct_change()
        raros = r[r.abs() > 0.08].index
        print(f"{col}: dias con movimiento > 8 %: {len(raros)}"
              + (f" ({', '.join(f'{d:%Y-%m-%d}' for d in raros[:12])})" if len(raros) else ""))
    for nombre, fecha in (("euro", EURO), ("mundial", MUNDIAL), ("EAFE con div.", EAFE_DIV), ("GC=F", GC_DESDE)):
        i = p.index.searchsorted(fecha)
        cambios = (p.iloc[i] / p.iloc[i - 1] - 1).abs()
        print(f"Empalme {nombre} ({p.index[i].date()}): mayor cambio de un dia {cambios[['bolsa', 'bonos', 'oro']].max():.4f}")


def main() -> None:
    p = montar()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    p.to_csv(SALIDA)
    print(f"{'serie':34} {'contra':26} {'desde':8} {'meses':>5} {'corr.':>7}  >= 0,95")
    for serie, contra, c, n, desde in comprobaciones(p):
        print(f"{serie:34} {contra:26} {desde:8} {n:5d} {c:7.3f}  {'si' if c >= UMBRAL else 'NO'}")
    calidad(p)


if __name__ == "__main__":
    main()
