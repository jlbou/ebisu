"""Inventario de datos historicos: fechas, huecos y ajuste por dividendos.

NO calcula rendimientos ni dibuja nada: mirar como fue el mercado en los anyos que seran la reserva la
contaminaria. Solo dice desde cuando hay datos, cuantos dias faltan y si el precio viene ajustado.

Uso: .venv/Scripts/python.exe estudios/inventario/inventario.py
Salida: datos en var/inventario/ (fuera de git) e informe en docs/estudios/inventario-datos.md.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import yfinance as yf

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "var" / "inventario"
INFORME = RAIZ / "docs" / "estudios" / "inventario-datos.md"

# (pieza, tipo, ticker, descripcion)
SERIES = [
    ("Bolsa", "larga", "VFINX", "Vanguard 500 Index (fondo, EE. UU.)"),
    ("Bolsa", "larga", "VTSMX", "Vanguard Total Stock Market Index (fondo, EE. UU.)"),
    ("Bolsa", "larga", "VGTSX", "Vanguard Total International Stock Index (fondo)"),
    ("Bolsa", "larga", "VT", "Vanguard Total World Stock ETF (EE. UU.)"),
    ("Bolsa", "larga", "ACWI", "iShares MSCI ACWI ETF (EE. UU.)"),
    ("Bolsa", "larga", "URTH", "iShares MSCI World ETF (EE. UU.)"),
    ("Bolsa", "real", "VWCE.DE", "Vanguard FTSE All-World UCITS, acumulacion (Xetra, EUR)"),
    ("Bolsa", "real", "EUNL.DE", "iShares Core MSCI World UCITS (Xetra, EUR)"),
    ("Bolsa", "real", "IWDA.AS", "iShares Core MSCI World UCITS (Amsterdam, EUR)"),
    ("Bonos", "larga", "VBMFX", "Vanguard Total Bond Market Index (fondo, EE. UU.)"),
    ("Bonos", "larga", "AGG", "iShares Core US Aggregate Bond ETF"),
    ("Bonos", "larga", "BNDX", "Vanguard Total International Bond ETF (cubierto a USD)"),
    ("Bonos", "real", "EUNA.DE", "iShares Core Global Aggregate Bond UCITS, cubierto a EUR (Xetra)"),
    ("Oro", "larga", "GC=F", "Futuro del oro (COMEX, continuo)"),
    ("Oro", "larga", "GLD", "SPDR Gold Shares (EE. UU.)"),
    ("Oro", "real", "4GLD.DE", "Xetra-Gold (EUR)"),
    ("Oro", "real", "EWG2.DE", "EUWAX Gold II (EUR)"),
    ("Monetario", "larga", "^IRX", "Rentabilidad de la letra del Tesoro de EE. UU. a 13 semanas (un tipo, no un precio)"),
    ("Monetario", "larga", "BIL", "SPDR Bloomberg 1-3 Month T-Bill ETF"),
    ("Monetario", "real", "XEON.DE", "Xtrackers II EUR Overnight Rate Swap UCITS (Xetra, EUR)"),
    ("Divisa", "larga", "EURUSD=X", "Cambio euro/dolar"),
]


def descargar(ticker: str) -> pd.DataFrame:
    destino = DATOS / f"{ticker.replace('^', '_').replace('=', '_')}.csv"
    df = yf.download(ticker, period="max", interval="1d", auto_adjust=False, progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna(how="all")
    if not df.empty:
        df.to_csv(destino)
    return df


def describir(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"primera": "-", "ultima": "-", "filas": 0, "faltan": "-", "hueco": "-", "ajuste": "sin datos"}
    fechas = pd.DatetimeIndex(df.index).normalize()
    habiles = pd.bdate_range(fechas.min(), fechas.max())
    faltan = len(habiles.difference(fechas))
    saltos = fechas.to_series().diff().dt.days.dropna()
    hueco = int(saltos.max()) if not saltos.empty else 0
    ajuste = "-"
    if "Adj Close" in df and "Close" in df:
        cociente = (df["Adj Close"] / df["Close"]).dropna()
        # Solo si el cociente cambia en el tiempo hay ajuste por repartos (no es un rendimiento).
        ajuste = "si (repartos)" if (cociente.max() - cociente.min()) > 1e-6 else "no (igual al cierre)"
    return {
        "primera": fechas.min().date().isoformat(),
        "ultima": fechas.max().date().isoformat(),
        "filas": len(df),
        "faltan": f"{faltan} ({faltan / max(len(habiles), 1):.1%})",
        "hueco": f"{hueco} dias",
        "ajuste": ajuste,
    }


def main() -> None:
    DATOS.mkdir(parents=True, exist_ok=True)
    filas = []
    for pieza, tipo, ticker, desc in SERIES:
        try:
            info = describir(descargar(ticker))
        except Exception as exc:  # una serie que falla no para el inventario
            info = {"primera": "-", "ultima": "-", "filas": 0, "faltan": "-", "hueco": "-", "ajuste": f"error: {exc}"[:80]}
        filas.append((pieza, tipo, ticker, desc, info))
        print(ticker, info)

    hoy = dt.date.today().isoformat()
    lineas = [
        f"# Inventario de datos historicos ({hoy})",
        "",
        "Generado por `estudios/inventario/inventario.py` con yfinance (no oficial). **Solo fechas, huecos y ajuste:",
        "no se ha calculado ningun rendimiento ni se ha mirado ninguna curva** (para no contaminar la reserva).",
        "",
        "- *Faltan*: dias habiles (lunes a viernes) sin precio entre la primera y la ultima fecha; incluye festivos.",
        "- *Hueco mayor*: el salto mas largo entre dos fechas con precio.",
        "- *Ajuste*: si el precio ajustado difiere del cierre (dividendos o cupones incluidos). Un ETF de acumulacion,",
        "  un futuro o un tipo de cambio no reparten: \"no\" es lo esperado ahi.",
        "",
        "| Pieza | Tipo | Ticker | Que es | Primera | Ultima | Filas | Faltan | Hueco mayor | Ajuste |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for pieza, tipo, ticker, desc, i in filas:
        lineas.append(
            f"| {pieza} | {tipo} | `{ticker}` | {desc} | {i['primera']} | {i['ultima']} | {i['filas']} | "
            f"{i['faltan']} | {i['hueco']} | {i['ajuste']} |"
        )
    INFORME.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("Informe:", INFORME)


if __name__ == "__main__":
    main()
