"""Informe de revision del bot en papel (docs/revision-3-dias.md): SOLO LEE `var/bot/`. No escribe, no avisa, no llama a
la IA. Lo lanza `deploy/revision.sh` en el VPS (como el usuario ebisu) para la revision de los 3 dias y las siguientes.

    python -m ebisu.revision [--desde 2026-10-15]
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from ebisu import estrategia as E
from ebisu import ia
from ebisu import papel as P
from ebisu import precios

RAIZ = Path(__file__).resolve().parents[1]
VAR = RAIZ / "var" / "bot"
GRAVES_PRECIOS = ("salto", "sin_precio")  # los mismos que el juez (ebisu/juez.py)


def _json(f: Path) -> dict:
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def informe(base: Path, desde: date, ahora: datetime) -> tuple[list[str], int]:
    """Las lineas del informe y el numero de cosas graves encontradas."""
    lineas, graves = [], 0
    hoy = pd.Timestamp(ahora.date())

    # 1. Vueltas: una buena cada dia, ninguna fallida
    lineas.append("== 1. Vueltas del dia")
    filas = []
    if (base / "vueltas.csv").exists():
        with (base / "vueltas.csv").open(encoding="utf-8") as h:
            filas = [r for r in csv.DictReader(h) if pd.Timestamp(r["fecha"]) >= pd.Timestamp(desde)]
    for d in pd.date_range(pd.Timestamp(desde), hoy):
        del_dia = [r for r in filas if pd.Timestamp(r["fecha"]) == d]
        malas = [r for r in del_dia if r["ok"] != "1"]
        if d == hoy and not del_dia and ahora.hour < 21:
            lineas.append(f"   {d:%d/%m}: todavia no (la primera es a las 20:05)")
            continue
        estado = "BIEN" if del_dia and not malas else "MAL"
        graves += estado == "MAL"
        lineas.append(f"   {d:%d/%m}: {estado}  {len(del_dia)} vueltas, {len(malas)} fallidas"
                      + (f" (primera {del_dia[0]['hora'][11:16]}, ultima {del_dia[-1]['hora'][11:16]})" if del_dia else ""))

    # 2. Avisos enviados por Telegram
    lineas.append("== 2. Avisos de Telegram (enviados y pendientes)")
    cola = _json(base / "cola.json")
    enviados, pendientes = cola.get("enviados", []), cola.get("pendientes", [])
    for e in enviados:
        clave = e.get("clave", e) if isinstance(e, dict) else e
        tipo = str(clave).split(":")
        grave = len(tipo) > 1 and tipo[0] == "precios" and tipo[1] in GRAVES_PRECIOS
        graves += grave
        lineas.append(f"   {'GRAVE' if grave else 'leve '}  {clave}")
    if not enviados:
        lineas.append("   ninguno")
    if pendientes:
        graves += 1
        lineas.append(f"   MAL: {len(pendientes)} aviso(s) sin poder enviar")

    # 3. Precios: completos y al dia
    lineas.append("== 3. Precios")
    cierres = precios.tabla(precios.leer(base / "precios.csv"))
    if cierres.empty:
        graves += 1
        lineas.append("   MAL: no hay precios guardados")
    else:
        recientes = cierres.loc[pd.Timestamp(desde) - pd.offsets.BDay(20):]
        huecos = recientes[recientes.isna().any(axis=1)]
        for d, f in huecos.iterrows():
            faltan = [k for k in f.index if pd.isna(f[k])]
            lineas.append(f"   hueco el {d:%d/%m/%Y}: {', '.join(faltan)}")
        ultimo = cierres.dropna().index[-1]
        retraso = len(pd.bdate_range(ultimo, hoy)) - 1
        graves += retraso >= precios.DIAS_SIN_PRECIO
        lineas.append("   BIEN  sin huecos en los ultimos 20 dias habiles" if huecos.empty else "   OJO   hay huecos (arriba)")
        lineas.append(f"   ultimo dia completo: {ultimo:%d/%m/%Y} ({retraso} dia(s) habil(es) de retraso)")

    # 4. Salud que apunta la vuelta
    lineas.append("== 4. Salud")
    estado = _json(base / "estado.json")
    ia_ok = estado.get("ia_version") == ia.VERSION_VERIFICADA
    latido_ok = estado.get("latido") is True
    graves += (not ia_ok) + (not latido_ok)
    lineas.append(f"   {'BIEN' if ia_ok else 'MAL '}  la IA responde ({estado.get('ia_version')})")
    lineas.append(f"   {'BIEN' if latido_ok else 'MAL '}  ultimo latido a Healthchecks ({estado.get('latido')})")
    lineas.append(f"   papel empezado: {'si' if estado.get('empezado') else 'no'}")

    # 5. Lo que haria la regla hoy
    lineas.append("== 5. La regla con los precios de hoy (como si fuera dia de senyal)")
    piezas = P.piezas_de(cierres) if not cierres.empty else pd.DataFrame()
    if len(piezas) >= max(E.MEDIAS):
        pesos = E.pesos_objetivo(piezas, P.H1M).iloc[-1]
        for k in P.PIEZAS:
            n = E.medias_superadas(piezas[k]).iloc[-1]
            lineas.append(f"   {k:<10} {int(n)} de 4 medias  peso {pesos[k]:.1%}")
        lineas.append(f"   {'monetario':<10}               peso {max(0.0, 1 - float(pesos.sum())):.1%}")
    return lineas, graves


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="2026-10-15")
    a = ap.parse_args()
    lineas, graves = informe(VAR, date.fromisoformat(a.desde), datetime.now(precios.MADRID))
    print("\n".join(lineas))
    print(f"== Resumen: {graves} cosa(s) grave(s) en los datos del bot")


if __name__ == "__main__":
    main()
