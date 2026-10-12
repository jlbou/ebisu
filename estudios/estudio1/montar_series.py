"""Monta las cuatro piezas de H1 en euros (docs/diseno-estudio-1.md, seccion 2) y hace la comprobacion de parecido.

Piezas (indices diarios, base 1 el primer dia; NO se ensenya ningun rendimiento):
- bolsa: 60 % VTSMX + 40 % VGTSX (precio ajustado), rebalanceado el primer dia habil de cada mes; sin cubrir.
- bonos: VBMFX (ajustado) cubierto a euros: rendimiento en dolares + (tipo del euro - tipo del dolar) por dias/360.
- oro: futuro del oro GC=F; sin cubrir.
- monetario: EONIA hasta el 30/09/2019 y STR desde el 01/10/2019 (BCE), devengo por dias naturales / 360.
Cambio: tipo de referencia del BCE (dolares por euro). Tipo del dolar: DTB3 de la Reserva Federal (seccion 9).

Comprobacion antes de medir (seccion 2): correlacion DIARIA >= 0,95 con los ETF reales desde que existen. Se da
tambien la semanal como informacion. Solo correlaciones: ni niveles, ni rendimientos, ni curvas.

Uso: .venv/Scripts/python.exe estudios/estudio1/montar_series.py
Salida: var/estudio1/piezas_eur.csv y un resumen por pantalla.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
INV = RAIZ / "var" / "inventario"
E1 = RAIZ / "var" / "estudio1"
INICIO = "2000-08-30"
FIN = "2026-09-30"
CAMBIO_STR = pd.Timestamp("2019-10-01")
UMBRAL = 0.95


def yahoo(nombre: str, col: str = "Adj Close") -> pd.Series:
    df = pd.read_csv(INV / f"{nombre}.csv", index_col=0, parse_dates=True)
    return df[col].astype(float).dropna()


def bce(nombre: str) -> pd.Series:
    df = pd.read_csv(E1 / f"bce_{nombre}.csv", index_col=0, parse_dates=True)
    return df["valor"].astype(float)


def devengo(tipo_pct: pd.Series, fechas: pd.DatetimeIndex) -> pd.Series:
    """Factor diario 1 + tipo * dias naturales / 360, con el tipo vigente el dia anterior."""
    t = tipo_pct.reindex(tipo_pct.index.union(fechas)).sort_index().ffill().reindex(fechas)
    dias = fechas.to_series().diff().dt.days.fillna(0).to_numpy()
    return pd.Series(1 + t.shift(1).fillna(0).to_numpy() / 100 * dias / 360, index=fechas)


def montar() -> pd.DataFrame:
    us, intl = yahoo("VTSMX"), yahoo("VGTSX")
    bonos_usd, oro_usd = yahoo("VBMFX"), yahoo("GC_F", "Close")
    fechas = us.index.intersection(intl.index).intersection(bonos_usd.index)
    fechas = fechas[(fechas >= INICIO) & (fechas <= FIN)]

    eurusd = bce("eurusd")
    fx = eurusd.reindex(eurusd.index.union(fechas)).sort_index().ffill().reindex(fechas)

    # Bolsa: 60/40 con rebalanceo el primer dia habil de cada mes (participaciones fijas dentro del mes).
    p_us, p_in = us.reindex(fechas), intl.reindex(fechas)
    valor, n_us, n_in, mes, bolsa_usd = 1.0, 0.0, 0.0, None, []
    for d in fechas:
        if d.month != mes:
            if mes is not None:
                valor = n_us * p_us[d] + n_in * p_in[d]
            n_us, n_in, mes = 0.6 * valor / p_us[d], 0.4 * valor / p_in[d], d.month
        bolsa_usd.append(n_us * p_us[d] + n_in * p_in[d])
    bolsa = pd.Series(bolsa_usd, index=fechas) / fx

    # Bonos cubiertos: rendimiento en dolares + diferencial de tipos.
    eur = pd.concat([bce("eonia")[bce("eonia").index < CAMBIO_STR], bce("estr")[bce("estr").index >= CAMBIO_STR]])
    dtb3 = pd.read_csv(E1 / "segunda_fuente" / "fred_DTB3.csv", index_col=0, parse_dates=True)["DTB3"].astype(float)
    r_usd = bonos_usd.reindex(fechas).pct_change().fillna(0)
    dif = devengo(eur, fechas) - devengo(dtb3, fechas)
    bonos = (1 + r_usd + dif).cumprod()

    oro = oro_usd.reindex(oro_usd.index.union(fechas)).sort_index().ffill().reindex(fechas) / fx
    monetario = devengo(eur, fechas).cumprod()

    piezas = pd.DataFrame({"bolsa": bolsa, "bonos": bonos, "oro": oro, "monetario": monetario})
    return piezas / piezas.iloc[0]


def parecido(piezas: pd.DataFrame) -> list[tuple]:
    reales = [("bolsa", "EUNL_DE"), ("bolsa", "VWCE_DE"), ("bonos", "EUNA_DE"), ("oro", "4GLD_DE"),
              ("monetario", "XEON_DE")]
    filas = []
    for pieza, etf in reales:
        real = yahoo(etf.replace("_DE", ".DE"), "Close")
        real = real[real.index <= FIN]
        comun = piezas.index.intersection(real.index)
        a, b = piezas[pieza].reindex(comun), real.reindex(comun)
        diaria = a.pct_change().corr(b.pct_change())
        semanal = a.resample("W-FRI").last().pct_change().corr(b.resample("W-FRI").last().pct_change())
        filas.append((pieza, etf.replace("_DE", ".DE"), comun.min().date(), len(comun), diaria, semanal))
    return filas


def main() -> None:
    piezas = montar()
    piezas.to_csv(E1 / "piezas_eur.csv")
    print(f"Piezas en euros: {piezas.index.min().date()} a {piezas.index.max().date()}, {len(piezas)} dias, "
          f"huecos: {int(piezas.isna().sum().sum())}")
    print(f"{'pieza':10} {'ETF real':9} {'desde':10} {'dias':>5} {'corr. diaria':>13} {'corr. semanal':>14}  >= 0,95")
    for pieza, etf, desde, n, d, s in parecido(piezas):
        print(f"{pieza:10} {etf:9} {desde!s:10} {n:5d} {d:13.3f} {s:14.3f}  {'si' if d >= UMBRAL else 'NO'}")


if __name__ == "__main__":
    main()
