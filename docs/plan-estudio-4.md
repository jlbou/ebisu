# Plan del estudio 4 (bolsa, bonos y oro, desde cero): todo antes de construir nada (14/10/2026, v2, PENDIENTE DE APROBAR)

Recoge la decision 14 (`docs/decisiones/14-replanteamiento.md`), la revision de la literatura
(`docs/estudios/recerca-activos-2.md`) y los datos (`docs/estudios/datos-antes-2000.md`). Version 2: integra las dos
revisiones (seccion 12). Skills usadas: `ml4t-case-study-development`, `ml4t-non-stationarity`,
`ml4t-backtest-overfitting`, `ml4t-point-in-time`, `ml4t-regime-awareness`, `ml4t-lookahead-bias`, `literature-review`.
**Nada medido. No se construye nada hasta que el propietario apruebe este plan.**

## 1. Lo decidido (resumen)

- Reglas por capas; H1 intacta como senyal; capa 6 opcional con scikit-learn, solo sobre la bolsa.
- Piezas de H1: bolsa (EE. UU. sola hasta 1996, mundial desde 1997), bonos de EE. UU. cubiertos a euros, oro, monetario
  en euros.
- Se juzga 1971-2026, y ademas 1990-2026; 1926-1970 solo informacion.
- Contra la bolsa mantenida: TAE >= la suya, o >= la suya - 1 punto con caida <= 2/3 de la suya.
- Tipos de mercado por anyos naturales: referencia en perdidas = bolsa a la baja; IPC de EE. UU. > 4 % = inflacion
  alta. En los anyos de bajada gana a la referencia; en los de subida, como mucho 5 puntos por detras.
- 5 variantes nuevas; N = 10 intentos contados.
- Impuestos con los tramos reales del ahorro de hoy.

## 2. Por que esta prueba es distinta de la del estudio 1

1. **Una sola medicion confirmatoria, sin exploracion.** Todas las reglas estan escritas antes de bajar los datos. El
   tramo 1971-2000 nunca se ha visto; 2001-2026 se conoce y por eso **no puede decidir solo**.
2. **Potencia calculada antes:** con N = 10 y un Sharpe real de 0,5 hacen falta ~41-55 anyos; hay 55.
3. **Todos los intentos cuentan**, tambien los del estudio 1 y 2 (H1-M, H1-S, H1-MB, H1-F, E2). Los de divisas (H2,
   diagnostico, fixing) **no**: otro mercado y otra hipotesis (dicho aqui para que no sea una decision escondida).
   Lo que se calcula solo como informacion no se usa para elegir nada y no cuenta.
4. **Datos tal como se conocian:** el IPC solo clasifica anyos al juzgar; en el modelo, el IPC de un mes solo se usa
   dos meses despues (CPIAUCNS, sin revisiones).
5. **Nada calculado con toda la historia:** volatilidades y medias con ventanas que solo miran atras; el modelo
   normaliza con lo aprendido en su entrenamiento (Pipeline de scikit-learn), nunca con datos posteriores.

## 3. Datos (todo en euros; diarios salvo lo dicho)

| Pieza | Hasta 1998 | Desde 1999 | Estado |
|---|---|---|---|
| Bolsa | EE. UU. con dividendos (Kenneth French, Mkt-RF + RF, diaria) hasta 1996 | Desde 1997: 60 % EE. UU. + 40 % MSCI EAFE (diaria). EAFE con dividendos solo desde 2001: en 1997-2000, precio diario + la diferencia mensual con el indice con dividendos de Kenneth French (International Indices), repartida por dias | French y MSCI comprobados |
| Bonos | Rentabilidad del bono de EE. UU. a **7 anyos** (FRED DGS7, diaria desde 07/1969) convertida en rendimiento: devengo + cambio de precio con la duracion de cada dia | Igual todo el periodo (una sola serie, sin empalmes) | DGS7 comprobado; contraste con VBMFX y EUNA |
| Cobertura a euros de los bonos | + (tipo corto aleman - letra a 3 meses de EE. UU., FRED DTB3) | + (EONIA/STR - DTB3) | DTB3 comprobado; tipo aleman por comprobar |
| Oro | Fixing de Frankfurt en marcos (Bundesbank, 1968-1998, comprobado) | 2001-2026 como en el estudio 1; **1999-2000 por resolver** | Hueco |
| Cambio | Marco/dolar diario del Bundesbank (desde 1948, comprobado); 1,95583 marcos por euro | BCE | Comprobado |
| Monetario | Tipo aleman a un dia (Bundesbank; si solo hay mensual, devengo diario con la media del mes) | EONIA y STR (BCE) | Por comprobar |
| Sectores (capa 6) | 49 sectores de EE. UU., mensuales desde 1926 (Kenneth French) | Igual | Comprobado |

- Calendario: union de dias habiles de Nueva York y Frankfurt; en festivo, el ultimo precio.
- **Comprobaciones antes de medir (no son medir):** cada serie reconstruida, donde coincida con el ETF real o con la
  serie del estudio 1, correlacion mensual >= 0,95. Si alguna falla, se para y se decide. Solo correlaciones.

## 4. Las 5 variantes (lista cerrada)

| # | Variante | Regla |
|---|---|---|
| 1 | **H1-M** | Tal cual `docs/diseno-estudio-1.md` 3 (medias de 20/50/100/200 dias, cuartos, mensual, ETF) |
| 2 | **H1-F** | Tal cual (fondos con traspaso, sin oro, ejecucion 6 dias habiles despues, impuestos al final) |
| 3 | **H1-M + capa 2 (volatilidad)** | Peso de cada pieza x min(1, vol. objetivo / vol. de los ultimos 63 dias). Vol. objetivo = mediana de la vol. de 63 dias de la pieza en los hasta 10 anyos anteriores (minimo 2; antes, factor 1). Nunca por encima del peso de H1-M |
| 4 | **H1-M + capa 3 (fiscal)** | Como H1-M, pero una pieza solo se **reduce** si su senyal baja 2 cuartos o mas, o llega a 0 |
| 5 | **La mejor de 1-4 + capa 6** | Seccion 5 |

"La mejor de 1-4" = la de mayor Sharpe en 1971-2026; elegirla despues de verla ya esta contado en N = 10.
Senyal al cierre del ultimo dia habil del mes; ejecucion al cierre del dia habil siguiente (fondos: 6 dias).

## 5. Capa 6: el modelo (un solo modelo, fijado antes)

- **Pregunta:** cuando la tendencia dice "dentro", ¿acertara el mes que viene? No predice el mercado.
- **Aprende de:** los 49 sectores, mensuales. Para cada sector y mes con precio por encima de su media de 10 meses,
  etiqueta = 1 si el mes siguiente gana mas que las letras del Tesoro, 0 si no.
- **Variables (con datos hasta el cierre del mes de la decision):** volatilidad de 3 y 12 meses; distancia a la media
  de 10 meses en unidades de volatilidad; cuantos de los plazos 1, 3, 6 y 12 meses son positivos; porcentaje de
  sectores por encima de su media; inflacion de EE. UU. a 12 meses de hace 2 meses.
- **Modelo:** regresion logistica (C = 1) en un Pipeline con la normalizacion; sin probar otros modelos ni valores.
- **Entrenamiento:** primero con 1927-1970 (no se juzgan); despues, cada enero, con todo lo anterior y 12 meses de
  separacion entre el ultimo dato de entrenamiento y su uso.
- **Como actua (solo la pieza de bolsa):** las variables se calculan con la pieza de bolsa **en dolares** (como los
  sectores); si la pieza tiene peso y la probabilidad es < 0,5, su peso se reduce a la mitad. Bonos y oro, sin tocar.
- **Control:** probabilidad de sobreajuste (PBO, validacion combinatoria de 8 grupos) entre {base, base + modelo}
  < 0,5; ninguna variable con mas del 40 % de la importancia.
- **Se queda solo si** la variante 5 pasa la seccion 7 **y** mejora el Sharpe de su base.

## 6. Costes, impuestos y referencia

- **Costes** (del estudio 1, `docs/diseno-estudio-1.md` 4): ETF 0 € de comision y 0,10 % por lado; gastos anuales
  de los ETF reales; fondos al 0,15 %.
- **Impuestos (P1):** tramos del ahorro de hoy (19 % hasta 6.000 €, 21 % hasta 50.000, 23 % hasta 200.000, 27 % hasta
  300.000, 30 % despues), sobre la ganancia neta de cada anyo; lotes, compensacion, arrastre de 4 anyos y regla de los
  dos meses (ETF); fondos, todo al final. Cada simulacion empieza con 250 € (los tramos, en euros de hoy, sin ajustar
  por inflacion: dicho en el veredicto).
- **Referencia:** la pieza de bolsa en un fondo indexado mantenido, impuesto al final con los mismos tramos.
- **Anacronismos (dichos en el veredicto):** ETF antes de 1993, traspasos antes de 2003 y la ley de hoy: se simula el
  vehiculo y las reglas de hoy.

## 7. Cuando pasa una variante (todas a la vez)

1. **1971-2026:** TAE despues de impuestos >= la de la referencia, o >= la de la referencia - 1 punto **y** caida
   maxima <= 2/3 de la suya (caida con el valor diario antes de impuestos pendientes, para las dos).
2. **1990-2026:** lo mismo, en una simulacion aparte que empieza el 01/01/1990 con la cuenta nueva (senyales
   calentadas con datos anteriores) y liquida al final; la referencia, igual.
3. **Tipos de mercado** (1971-2025, anyos completos, rendimientos antes de impuestos): media de (estrategia -
   referencia) > 0 en los anyos de bolsa a la baja, por separado con inflacion alta y baja; >= -5 puntos en los de
   subida, por separado. Si un tipo tiene menos de 3 anyos, se junta con el de la misma direccion de bolsa (P3).
4. **No es suerte (solo 1971-2026):** Sharpe deflactado del exceso mensual sobre el monetario (neto de costes, antes de
   impuestos, con asimetria y colas) >= 0,95, con N = 10 y la varianza de los Sharpe de las 5 variantes nuevas (si es
   menor que la de pura suerte, la de pura suerte).
5. Solo la variante 5: seccion 5.

Si pasan varias: la de mayor Sharpe deflactado; si la diferencia es < 0,02, la automatica (ETF) antes que la de fondos.

**Solo informacion (no decide):** cada condicion en 1971-2000 sola (el tramo limpio); la pieza de bolsa con la regla
de H1 en 1927-1970; la bolsa fuera de EE. UU. mensual en 1975-1996; cuantos anyos tiene cada tipo de mercado.

## 8. Pre-mortem

| Que podria fallar | Prevision |
|---|---|
| Un error al reconstruir una serie decide el resultado | Comprobaciones de la seccion 3; validaciones con datos inventados (seccion 10) |
| El bono aproximado no se parece al real | Contraste con VBMFX/EUNA; si no llega a 0,95, se para |
| Antes de 1997 solo hay bolsa de EE. UU. | Dicho; la mensual de fuera de EE. UU. como informacion |
| Un tipo de mercado con muy pocos anyos | Regla P3, fijada antes |
| Pasa por 1971-2000 pero no por los anyos recientes | Condicion 2 (1990-2026) |
| Caidas rapidas con rebote (1987, 2020) | Debilidad conocida; se ve por anyos |
| Tentacion de retocar tras ver resultados | Prohibido: una medicion; cualquier cambio es un estudio nuevo con N + 1 |

## 9. Si pasa / si no pasa

- **Si pasa una:** papel (decision 11) con la IA en sombra (decision 8); dinero real solo con el si del propietario.
- **Si no pasa ninguna:** se escribe por que y se sigue con el laboratorio de divisas en papel (decision 14.1). No se
  vuelve a medir 1971-2026 con variaciones de estas reglas.

## 10. Orden de trabajo (cada paso, con el OK del propietario)

1. Comprobar fuentes: tipo aleman a un dia, oro 1999-2000, tramos en la web de la AEAT.
2. Bajar y montar las series; comprobaciones de correlacion (seccion 3).
3. Simulador y validaciones con datos inventados calculados a mano: rendimiento del bono con duracion, cobertura,
   tramos de impuestos y regla de los dos meses, capa 2, capa 3, agrupacion por tipos de mercado, Sharpe deflactado,
   modelo sin datos futuros (una variable que mira el futuro tiene que dar error).
4. Medir una vez (`--medir --confirmo`) y escribir el veredicto.

## 11. Lo que no se ha comprobado

Los tramos (fuentes secundarias), el tipo aleman a un dia, el oro de 1999-2000, que la serie de bonos reconstruida se
parezca al indice real, y las cifras de la literatura leidas por resumenes.

## 12. Historial de revisiones

**Revision 1 (14/10):** 12 correcciones tecnicas (simulacion aparte para 1990-2026; tipos de mercado antes de
impuestos; Sharpe mensual; ventana creciente en la capa 2; cambio del Bundesbank desde 1948; bono a 7 anyos;
calendario comun; PBO entre base y base + modelo; sin pendiente de tipos; anacronismos; fuentes; tipos de mercado
solo para juzgar) y tres decisiones del propietario: P1 tramos reales, P2 modelo solo en bolsa, P3 juntar tipos con
menos de 3 anyos.

**Revision 2 (final, 14/10, skill `ml4t-lookahead-bias`):**

| # | Agujero | Correccion |
|---|---|---|
| F1 | MSCI EAFE con dividendos gratis solo desde 2001 | 1997-2000: precio diario + diferencia mensual con Kenneth French |
| F2 | El texto mezclaba el bono a 10 anyos con el empalme con VBMFX | Una sola serie a 7 anyos todo el periodo |
| F3 | El modelo aprende en dolares y la pieza esta en euros | Variables del modelo con la pieza en dolares |
| F4 | Normalizar con ventanas en el modelo podia mezclar datos | Pipeline: la normalizacion se ajusta solo con el entrenamiento |
| F5 | No se decia sobre que valor se mide la caida | Valor diario antes de impuestos pendientes, para las dos |
| F6 | No se decia en que tramo se calcula el Sharpe deflactado | Solo 1971-2026 (la potencia esta calculada para 55 anyos) |
| F7 | Los tramos de hoy aplicados a 250 € de 1971 | Se dice en el veredicto; no se ajusta |
| F8 | Lo calculado como informacion podia influir | No se usa para elegir nada; no cuenta como intento |
| F9 | Faltaba la lista de validaciones | Seccion 10.3 |
