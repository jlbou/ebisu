"""Validacion del simulador ANTES de medir (docs/diseno-estudio-1.md, seccion 7, paso 4).

Todo con datos SINTETICOS (inventados), para no ver ni un numero real. Cada prueba compara el simulador con una
cuenta hecha aparte, a mano. Sale "OK" o "FALLA" con la diferencia; si falla alguna, no se mide nada.

Uso: .venv/Scripts/python.exe estudios/estudio1/validar.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulador import TIPO, Variante, medias_superadas, referencia, simular  # noqa: E402

FALLOS: list[str] = []


def comprobar(nombre: str, obtenido: float, esperado: float, tol: float = 1e-10) -> None:
    ok = abs(obtenido - esperado) <= tol
    print(f"{'OK   ' if ok else 'FALLA'} {nombre}: obtenido {obtenido:.12f}, esperado {esperado:.12f}")
    if not ok:
        FALLOS.append(nombre)


def piezas_sinteticas(semilla: int = 7, dias: int = 900) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    fechas = pd.bdate_range("2001-01-01", periods=dias)
    datos = {a: 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, dias))) for a in ("bolsa", "bonos", "oro")}
    datos["monetario"] = 100 * np.cumprod(np.full(dias, 1.0001))
    return pd.DataFrame(datos, index=fechas)


def main() -> None:
    pz = piezas_sinteticas()
    ini, fin = str(pz.index[0].date()), str(pz.index[-1].date())

    # 1. Con pesos fijos (todo en bolsa desde el primer dia) y sin costes, da EXACTAMENTE comprar y mantener.
    for fondos in (True, False):
        v = Variante("fijo", fondos=fondos, piezas=("bolsa",), coste_lado=0.0, calendario={ini: {"bolsa": 1.0}})
        r, ref = simular(pz, v, ini, fin), referencia(pz, ini, fin)
        etiqueta = "fondos" if fondos else "ETF"
        comprobar(f"1. comprar y mantener ({etiqueta}): bolsillo", r.bolsillo, ref.bolsillo)
        comprobar(f"1. comprar y mantener ({etiqueta}): peor diferencia diaria", float((r.valor - ref.valor).abs().max()), 0.0)

    # 2. Costes: todo en bolsa con 0,10 % por lado. A mano: entrar al monetario (1 lado), salir de el y comprar bolsa
    #    (2 lados), vender al final (1 lado); impuesto sobre la ganancia neta de comisiones.
    c = 0.001
    v = Variante("costes", piezas=("bolsa",), coste_lado=c, calendario={ini: {"bolsa": 1.0}})
    r = simular(pz, v, ini, fin)
    b0, bT = pz["bolsa"].iloc[0], pz["bolsa"].iloc[-1]
    unidades = (1 - c) / (b0 * (1 + c) ** 2)
    venta = unidades * bT * (1 - c)
    base = 1.0  # lo que salio del bolsillo: el monetario se vendio al mismo precio (sin perdida ni ganancia neta)
    # La compra de bolsa cuesta unidades * b0 * (1 + c); la perdida del monetario (sus comisiones) compensa.
    esperado = venta - TIPO * max(venta - base, 0)
    comprobar("2. costes del 0,10 % por lado e impuesto al final", r.bolsillo, esperado, 1e-9)

    # 3. Impuestos por anyos: ganancia el 2001 (paga ese anyo); perdida el 2002 (se arrastra); ganancia el 2003 (se
    #    compensa con la perdida arrastrada).
    f = pd.bdate_range("2001-01-01", "2003-12-31")
    precio = pd.Series(100.0, index=f)
    precio[f >= "2001-06-01"] = 150.0
    precio[f >= "2002-03-01"] = 120.0
    precio[f >= "2002-09-02"] = 90.0
    precio[f >= "2003-06-02"] = 110.0
    pz3 = pd.DataFrame({"bolsa": precio, "bonos": 100.0, "oro": 100.0, "monetario": 100.0}, index=f)
    cal = {"2001-01-01": {"bolsa": 1.0}, "2001-10-01": {"bolsa": 0.0},  # 100 -> 150 y fuera (2001)
           "2002-03-01": {"bolsa": 1.0}, "2002-09-02": {"bolsa": 0.0},  # 120 -> 90 y fuera (2002)
           "2003-03-03": {"bolsa": 1.0}}  # 90 -> 110 hasta el final (2003)
    r = simular(pz3, Variante("impuestos", piezas=("bolsa",), coste_lado=0.0, calendario=cal), "2001-01-01", "2003-12-31")
    imp_2001 = TIPO * 0.5
    valor_2002 = 1.5 - imp_2001
    perdida_2002 = valor_2002 * (90 / 120 - 1)
    valor_2003 = valor_2002 + perdida_2002
    ganancia_2003 = valor_2003 * (110 / 90 - 1)
    imp_2003 = TIPO * max(ganancia_2003 + perdida_2002, 0)
    comprobar("3. impuestos: pagados en total", r.impuestos, imp_2001 + imp_2003)
    comprobar("3. impuestos: bolsillo", r.bolsillo, valor_2003 + ganancia_2003 - imp_2003)

    # 4. Regla de los dos meses: ganancia en marzo; perdida en junio. Si se recompra a las 3 semanas, la perdida se
    #    aplaza y en 2001 se paga por la ganancia; si se recompra a los 3 meses, la perdida compensa y no se paga.
    precio = pd.Series(100.0, index=f)
    precio[f >= "2001-03-01"] = 120.0
    precio[f >= "2001-05-01"] = 80.0
    precio[f >= "2002-01-02"] = 100.0
    pz4 = pd.DataFrame({"bolsa": precio, "bonos": 100.0, "oro": 100.0, "monetario": 100.0}, index=f)
    base = {"2001-01-01": {"bolsa": 0.5}, "2001-03-01": {"bolsa": 0.0}, "2001-04-02": {"bolsa": 0.5},
            "2001-06-01": {"bolsa": 0.0}}
    con = simular(pz4, Variante("con", piezas=("bolsa",), coste_lado=0.0, calendario={**base, "2001-06-22": {"bolsa": 0.5}}),
                  "2001-01-01", "2003-12-31")
    sin = simular(pz4, Variante("sin", piezas=("bolsa",), coste_lado=0.0, calendario={**base, "2001-09-03": {"bolsa": 0.5}}),
                  "2001-01-01", "2003-12-31")
    ganancia_marzo = 0.5 * 0.2
    fin_2001 = pd.Timestamp("2001-12-31")
    comprobar("4. dos meses: con recompra en 3 semanas paga la ganancia de marzo en 2001",
              float(sin.valor[fin_2001] - con.valor[fin_2001]), TIPO * ganancia_marzo)
    # Totales a mano. Tras marzo hay 1,1; en abril 0,55 a 120; en junio se vende a 80 (perdida 0,18333) y quedan
    # 0,91667; se recompra la mitad (0,45833) a 80 y al final vale a 100: ganancia 0,11458.
    perdida_junio = 0.55 * (80 / 120 - 1)
    ganancia_final = 0.5 * (1.1 + perdida_junio) * (100 / 80 - 1)
    # Con recompra: 2001 paga la ganancia de marzo; al final la perdida aplazada (mayor que la ganancia) deja 0.
    comprobar("4. dos meses: total con recompra", con.impuestos,
              TIPO * ganancia_marzo + TIPO * max(ganancia_final + perdida_junio, 0))
    # Sin recompra: 2001 queda en perdida neta (se arrastra) y compensa la ganancia final.
    comprobar("4. dos meses: total sin recompra", sin.impuestos,
              TIPO * max(ganancia_final + (ganancia_marzo + perdida_junio), 0))

    # 5. Senyal: una serie que solo sube supera las 4 medias; una que solo baja, ninguna; antes de 200 dias, nada.
    sube = pd.Series(np.linspace(1, 2, 400), index=pd.bdate_range("2001-01-01", periods=400))
    baja = pd.Series(np.linspace(2, 1, 400), index=sube.index)
    comprobar("5. senyal: serie que sube -> 4", float(medias_superadas(sube).iloc[-1]), 4.0)
    comprobar("5. senyal: serie que baja -> 0", float(medias_superadas(baja).iloc[-1]), 0.0)
    comprobar("5. senyal: dia 199 sin calcular", float(medias_superadas(sube).iloc[198:199].isna().sum()), 1.0)

    # 6. El monetario nunca queda en negativo (sin apalancamiento), con la regla real y costes.
    v = Variante("H1-M", coste_lado=0.001)
    r = simular(pz, v, str(pz.index[260].date()), fin)
    comprobar("6. sin apalancamiento: valor minimo > 0", float(r.valor.min() > 0), 1.0)

    print()
    print("VALIDACION:", "TODO OK" if not FALLOS else f"FALLAN {len(FALLOS)}: {', '.join(FALLOS)}")
    sys.exit(1 if FALLOS else 0)


if __name__ == "__main__":
    main()
