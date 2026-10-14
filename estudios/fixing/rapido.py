"""Prueba rapida del fixing (docs/diseno-fixing-rapido.md): una sola medicion, 2020-2026, EUR/USD y USD/JPY.

  --validar               caso inventado calculado a mano
  --medir --confirmo      mide una vez y escribe docs/estudios/fixing-rapido.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
VEREDICTO = RAIZ / "docs" / "estudios" / "fixing-rapido.md"
TRAMO = ("2020-01-01", "2026-09-30")
SIGNO = {"EURUSD": 1, "USDJPY": -1}  # rendimiento de la divisa extranjera contra el dolar
MIN_PB, MIN_T = 2.5, 2.5


def precios(h: pd.DataFrame) -> pd.DataFrame:
    """Precio medio al empezar cada hora de Nueva York (apertura de la vela), por fecha y hora de Nueva York."""
    ny = h.index.tz_convert("America/New_York")
    mid = (h["bid_o"] + h["ask_o"]) / 2
    df = pd.DataFrame({"fecha": pd.DatetimeIndex(ny.date), "hora": ny.hour, "verano": [bool(x.dst()) for x in ny],
                       "p": np.log(mid.to_numpy())})
    return df.drop_duplicates(["fecha", "hora"]).set_index(["fecha", "hora"])


def reversiones(pr: pd.DataFrame, signo: int, desde: str, hasta: str) -> pd.DataFrame:
    """Por dia d (el que acaba a las 17:00 de Nueva York): reversion de Tokio y de Europa, en pb."""
    p = pr["p"]
    out = []
    for d in pd.bdate_range(desde, hasta):
        ayer = d - pd.Timedelta(days=1)  # el dia empieza a las 17:00 de la vispera (el lunes, el domingo)
        try:
            verano = bool(pr.loc[(ayer, 18), "verano"])
            hora_fix = 21 if verano else 20
            p18, pfix, p2 = p[(ayer, 18)], p[(ayer, hora_fix)], p[(d, 2)]
            p8, p11, p16 = p[(d, 8)], p[(d, 11)], p[(d, 16)]
        except KeyError:
            continue
        tokio = -(pfix - p18) + (p2 - pfix)
        europa = -(p8 - p2) + (p16 - p11)
        out.append({"dia": d, "tokio": signo * tokio * 1e4, "europa": signo * europa * 1e4})
    return pd.DataFrame(out).set_index("dia")


def resumen(x: pd.Series) -> dict:
    n = len(x)
    media = float(x.mean())
    t = media / (float(x.std(ddof=1)) / np.sqrt(n))
    return {"dias": n, "media_dia": media, "por_operacion": media / 2, "t": t,
            "sigue": bool(media / 2 >= MIN_PB and t >= MIN_T)}


def validar() -> bool:
    # Un dia (martes 14/01/2025, invierno): precio 1,0000 salvo: 20:00 del lunes 0,9990 (cae antes de Tokio y vuelve:
    # -(-10 pb) + (+10 pb) = 20 pb aprox.), 8:00 del martes 0,9980 (cae antes del BCE: +20 pb aprox.), 16:00 1,0010.
    idx = pd.date_range("2025-01-13 17:00", "2025-01-14 17:00", freq="h", tz="America/New_York", inclusive="left")
    v = pd.Series(1.0, index=idx)
    v[pd.Timestamp("2025-01-13 20:00", tz="America/New_York")] = 0.9990
    v[pd.Timestamp("2025-01-14 08:00", tz="America/New_York")] = 0.9980
    v[pd.Timestamp("2025-01-14 16:00", tz="America/New_York")] = 1.0010
    h = pd.DataFrame({"bid_o": v.to_numpy(), "ask_o": v.to_numpy()}, index=idx.tz_convert("UTC"))
    r = reversiones(precios(h), 1, "2025-01-14", "2025-01-14")
    ok_t = abs(r["tokio"].iloc[0] - 2 * (-np.log(0.9990)) * 1e4) < 1e-9
    esperado_e = (-np.log(0.9980) + np.log(1.0010)) * 1e4  # -(p8 - p2) + (p16 - p11)
    ok_e = abs(r["europa"].iloc[0] - esperado_e) < 1e-9
    print(f"{'OK   ' if ok_t else 'FALLA'} Tokio: {r['tokio'].iloc[0]:.6f} pb")
    print(f"{'OK   ' if ok_e else 'FALLA'} Europa: {r['europa'].iloc[0]:.6f} pb, esperado {esperado_e:.6f}")
    return ok_t and ok_e


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--medir", action="store_true")
    ap.add_argument("--confirmo", action="store_true")
    a = ap.parse_args()
    if a.validar:
        sys.exit(0 if validar() else 1)
    if not (a.medir and a.confirmo):
        sys.exit("Para medir: --medir --confirmo (una sola vez). Para probar: --validar.")
    if VEREDICTO.exists():
        sys.exit(f"Ya hay un veredicto ({VEREDICTO.name}): no se vuelve a medir.")
    sys.path.insert(0, str(AQUI.parent / "h2reserva"))
    sys.path.insert(0, str(AQUI.parent / "estudio1"))
    from h2_horas import horas_de_par
    lin = ["# Prueba rapida del fixing (2020-2026)", "",
           "Generado por `estudios/fixing/rapido.py` con el criterio de `docs/diseno-fixing-rapido.md`. Una vez.", "",
           "| Par | Grupo | Dias | Media por dia | Por operacion | t | Sigue (>= 2,5 pb y t >= 2,5) |",
           "|---|---|---|---|---|---|---|"]
    alguno = False
    for par, signo in SIGNO.items():
        h = horas_de_par(par).loc["2019-12-25":"2026-10-01"]
        r = reversiones(precios(h), signo, *TRAMO)
        for grupo in ("tokio", "europa"):
            s = resumen(r[grupo])
            alguno |= s["sigue"]
            lin.append(f"| {par} | {grupo} | {s['dias']} | {s['media_dia']:+.2f} pb | {s['por_operacion']:+.2f} pb | "
                       f"{s['t']:.2f} | {'SI' if s['sigue'] else 'no'} |")
        anual = r.groupby(r.index.year).mean() / 2
        lin += ["", f"{par}, efecto por operacion y anyo (informacion): "
                + "; ".join(f"{y}: Tokio {f['tokio']:+.2f}, Europa {f['europa']:+.2f}" for y, f in anual.iterrows())
                + " (pb).", ""]
    lin += ["", f"**Veredicto: {'SIGUE: vale la pena disenyar el estudio completo' if alguno else 'NO SIGUE: se para'}.**"]
    VEREDICTO.write_text("\n".join(lin) + "\n", encoding="utf-8")
    print(VEREDICTO.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
