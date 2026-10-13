# Estudio 3: diagnostico (puerta 1)

Generado por `estudios/estudio3/diagnostico.py` con el criterio de `docs/plan-estudio-3.md` (seccion 4).
Los 7 pares principales, 2003-2026 (ya vistos): solo dice si vale la pena seguir. Barreras provisionales:
objetivo en la mitad del rango de ayer, stop de 1 rango medio, maximo 5 dias. Resultado neto por operacion
(fraccion del nominal, sin apalancamiento ni impuestos).

Operaciones: 27315 (compras 13538, ventas 13777); media de todas: -0.1363%.

| | Valor | Necesario | Cumple |
|---|---|---|---|
| Media de las no marcadas | -0.1134% (mediana +0.1629%) | > 0 | NO |
| Parte no marcada | 34.4% | >= 40 % | NO |
| Peores (5 %) marcadas | 69.6% | >= 50 % | si |

Por escenario (una operacion puede tener varios):

| Escenario | Operaciones | Media | Parte de la perdida total |
|---|---|---|---|
| evento | 6495 | -0.1614% | 25.6% |
| tendencia | 10676 | -0.1423% | 39.4% |
| volatilidad | 770 | -0.1371% | 3.5% |
| miedo | 3100 | -0.1587% | 14.2% |
| rotura | 5744 | -0.1971% | 24.2% |
| ninguno | 9386 | -0.1134% | 31.5% |

Informacion (no decide): por sentido y por par, media de las no marcadas.

| | Operaciones no marcadas | Media |
|---|---|---|
| compras | 4725 | -0.0993% |
| ventas | 4661 | -0.1277% |
| AUDUSD | 1294 | -0.1084% |
| EURUSD | 1270 | -0.0953% |
| GBPUSD | 1358 | -0.1135% |
| NZDUSD | 1441 | -0.1551% |
| USDCAD | 1346 | -0.0940% |
| USDCHF | 1406 | -0.1177% |
| USDJPY | 1271 | -0.1051% |

Motivos de salida: objetivo 13209, stop 8496, viernes 5607, tiempo 3.

**Veredicto: NO PASA la puerta: se para.**
