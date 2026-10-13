"""H2 con el orden real de las horas: SOLO INFORMACION, no cambia ningun veredicto (docs/diseno-h2-reserva.md, "Despues").

Con velas diarias, el ~23 % de los dias en que se compra tambien se toca el maximo de ayer y no se sabe que fue antes;
el criterio contaba lo peor. Aqui se recorren las velas de 1 hora de Dukascopy: se compra en la primera hora en que el
ask toca el minimo de ayer; se vende en la primera hora POSTERIOR en que el bid toca el maximo de ayer; si no, al
cierre. Si en la misma hora de la compra tambien se toca el maximo, sigue sin saberse el orden: se dan las dos cotas
(peor: esa hora no vende; mejor: vende al maximo de ayer).

Uso: .venv/Scripts/python.exe estudios/h2reserva/h2_horas.py   (escribe docs/estudios/h2-horas.md)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "estudio1"))
import h2  # noqa: E402
from juez import metricas  # noqa: E402

RAIZ = AQUI.parents[1]
PIEZAS = RAIZ / "var" / "estudio1" / "piezas_eur.csv"
SALIDA = RAIZ / "docs" / "estudios" / "h2-horas.md"
TRAMOS = {"exploracion": ("2003-08-05", "2014-12-31"), "reserva": ("2015-01-01", "2026-09-30")}


def horas_de_par(par: str) -> pd.DataFrame:
    divisor = 1e3 if par.endswith("JPY") else 1e5
    lados = {}
    for lado in ("BID", "ASK"):
        trozos = []
        for f in sorted((h2.DUKAS / par).glob(f"*_{lado}.bi5")):
            inicio = pd.Timestamp(year=int(f.name[:4]), month=int(f.name[5:7]), day=1, tz="UTC")
            trozos.append(h2.leer_mes(f, divisor, inicio))
        lados[lado.lower()] = pd.concat([x for x in trozos if len(x)]).sort_index()
    h = lados["bid"].add_prefix("bid_").join(lados["ask"].add_prefix("ask_"), how="inner")
    h["dia"] = pd.DatetimeIndex((h.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)).date)
    return h


def operaciones_horas(h: pd.DataFrame, optimista: bool) -> tuple[pd.Series, pd.Series]:
    """Rendimiento de cada operacion con el orden de las horas (mismos niveles que h2.operaciones)."""
    d = h.groupby("dia").agg(ask_l=("ask_l", "min"), bid_h=("bid_h", "max"), bid_c=("bid_c", "last"))
    nivel = d.shift(1)[["ask_l", "bid_h"]].rename(columns={"ask_l": "min_ayer", "bid_h": "max_ayer"})
    x = h.join(nivel, on="dia").dropna(subset=["min_ayer"])
    x["n"] = x.groupby("dia").cumcount()
    toca_min = x["ask_l"] <= x["min_ayer"]
    toca_max = x["bid_h"] >= x["max_ayer"]
    entrada = x["n"].where(toca_min).groupby(x["dia"]).min()
    x = x.join(entrada.rename("n_entra"), on="dia")
    sale_despues = (toca_max & (x["n"] > x["n_entra"])).groupby(x["dia"]).any()
    misma_hora = (toca_max & (x["n"] == x["n_entra"])).groupby(x["dia"]).any()
    dias = entrada.dropna().index
    vende_max = sale_despues.reindex(dias) | (misma_hora.reindex(dias) & optimista)
    salida = np.where(vende_max, nivel["max_ayer"].reindex(dias), d["bid_c"].reindex(dias))
    return pd.Series(salida / nivel["min_ayer"].reindex(dias).to_numpy() - 1, index=dias), misma_hora.reindex(dias)


def main() -> None:
    piezas = pd.read_csv(PIEZAS, index_col=0, parse_dates=True)
    mon = piezas["monetario"]
    ops = {"peor": {}, "mejor": {}}
    ambiguas = {}
    dias_fx = {}
    for p in h2.PARES:
        h = horas_de_par(p)
        for cota, opt in (("peor", False), ("mejor", True)):
            ops[cota][p], amb = operaciones_horas(h, opt)
        ambiguas[p] = float(amb.mean())
        dias_fx[p] = h2.dias_de_par(p)
        print(p, "listo", flush=True)
    dias = sorted(set().union(*(d.index for d in dias_fx.values())))
    mon_fx = mon.reindex(mon.index.union(pd.DatetimeIndex(dias))).ffill().reindex(pd.DatetimeIndex(dias))
    original = h2.operaciones
    lin = ["# H2 con el orden real de las horas (SOLO INFORMACION)", "",
           "Generado por `estudios/h2reserva/h2_horas.py`. **No cambia ningun veredicto**: los dos tramos ya estaban vistos",
           "(estudio 1 y `docs/estudios/h2-reserva.md`). Mismas reglas, costes e impuestos que H2; solo cambia saber que",
           "se toco antes, el minimo o el maximo de ayer, mirando las velas de 1 hora.", "",
           "| Tramo | Calculo | TAE neta | Caida max. | Media por operacion |", "|---|---|---|---|---|"]
    for tramo, (ini, fin) in TRAMOS.items():
        for cota in ("diario (criterio)", "peor", "mejor"):
            if cota == "diario (criterio)":
                h2.operaciones = original
            else:
                h2.operaciones = lambda d, c=cota: ops[c][d.attrs["par"]]
            for p, d in dias_fx.items():
                d.attrs["par"] = p
            r = h2.simular_h2(dias_fx, mon_fx, ini, fin)
            m = metricas(r.valor, r.bolsillo, mon_fx)
            media = float(np.concatenate(list(r.por_operacion.values())).mean())
            lin.append(f"| {tramo} {ini[:4]}-{fin[:4]} | {cota} | {m.tae:.2%} | {m.caida:.1%} | {media:+.4%} |")
    h2.operaciones = original
    lin += ["", "Compras en que la misma hora toca tambien el maximo (orden desconocido incluso por horas):", ""]
    lin += [f"- {p}: {v:.1%}" for p, v in ambiguas.items()]
    SALIDA.write_text("\n".join(lin) + "\n", encoding="utf-8")
    print(SALIDA.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
