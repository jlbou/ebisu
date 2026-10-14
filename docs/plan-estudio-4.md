# Plan del estudio 4 (bolsa, bonos y oro, desde cero): todo antes de construir nada (14/10/2026, BORRADOR)

Recoge la decision 14 (`docs/decisiones/14-replanteamiento.md`) y la revision de la literatura
(`docs/estudios/recerca-activos-2.md`, `docs/estudios/datos-antes-2000.md`). Skills usadas para el plan:
`ml4t-case-study-development`, `ml4t-non-stationarity`, `ml4t-backtest-overfitting`, `ml4t-point-in-time`,
`literature-review`. **Nada medido. No se construye nada hasta que el propietario apruebe este plan.**

## 1. Lo decidido (resumen)

- Reglas por capas; H1 intacta como senyal; capa 6 opcional con scikit-learn.
- Piezas de H1: bolsa (EE. UU. sola hasta 1996, mundial desde 1997), bonos de EE. UU. cubiertos a euros, oro, monetario
  en euros.
- Se juzga 1971-2026, y ademas 1990-2026; 1926-1970 solo informacion.
- Contra la bolsa mantenida: TAE >= la suya, o >= la suya - 1 punto con caida <= 2/3 de la suya.
- Tipos de mercado por anyos: referencia en perdidas = bolsa a la baja; IPC de EE. UU. > 4 % = inflacion alta. En
  los anyos de bajada gana a la referencia (media anual); en los de subida, como mucho 5 puntos por detras.
- 5 variantes nuevas; 10 intentos contados en total.

## 2. Por que esta prueba es distinta de la del estudio 1 (lo que dicen las skills)

1. **Una sola medicion confirmatoria, sin exploracion** (backtest-overfitting). Todas las reglas salen de documentos ya
   escritos (H1, del 12/10) o se fijan aqui antes de bajar los datos. No hay nada que ajustar mirando resultados: el
   tramo 1971-2000 nunca se ha visto y hace de prueba limpia; 2001-2026 se conoce y por eso **no puede decidir solo**.
2. **Potencia calculada antes** (`datos-antes-2000.md`): con N = 10 y un Sharpe real de 0,5 hacen falta ~41-55 anyos;
   hay 55.
3. **Todos los intentos cuentan**, tambien los del estudio 1 y 2 (H1-M, H1-S, H1-MB, H1-F, E2). Los de divisas (H2,
   diagnostico, fixing) **no** se cuentan: son otro mercado y otra hipotesis; se dice aqui para que no sea una
   decision escondida.
4. **Datos tal como se conocian** (point-in-time): el IPC solo se usa para clasificar anyos al juzgar, no para operar;
   en el modelo de la capa 6, el IPC de un mes solo esta disponible al final del mes siguiente (se usa el IPC sin
   desestacionalizar, CPIAUCNS, que no se revisa).
5. **Nada calculado con toda la historia** (non-stationarity): volatilidades, medias y normalizaciones con ventanas
   que solo miran atras.

## 3. Datos (todo en euros; diarios salvo lo dicho)

| Pieza | 1971-1998 | 1999-2026 | Comprobado |
|---|---|---|---|
| Bolsa | EE. UU. con dividendos (Kenneth French, Mkt-RF + RF, diaria) hasta 1996 | Mundial desde 1997: 60 % EE. UU. + 40 % MSCI EAFE con dividendos (gratis desde 1997) | French y MSCI, si; MSCI EAFE con dividendos diaria desde 2001 en la prueba (antes, sin dividendos: **por comprobar**) |
| Bonos | Rentabilidad del bono de EE. UU. a 10 anyos (FRED DGS10, diaria desde 1962) convertida en rendimiento (cupon + efecto de la duracion) | Igual, hasta enlazar con la serie del estudio 1 (VBMFX) | DGS10, si; **la conversion es una aproximacion**: se contrasta con VBMFX en 1987-2026 |
| Cobertura a euros de los bonos | Diferencia de tipos a corto: aleman (marco) frente a EE. UU. | EONIA/STR frente a EE. UU. | Tipos alemanes diarios **por comprobar** (Bundesbank) |
| Oro | Fixing de Frankfurt en marcos (Bundesbank, 1968-1998) | Desde 1999: **hueco 1999-2000 por resolver** (fixing de Londres en dolares + cambio) | Frankfurt, si |
| Cambio | Marco/dolar (FRED DEXGEUS, diario 1971-2001); marco fijo a 1,95583 por euro | BCE | DEXGEUS, si |
| Monetario | Tipo aleman a un dia (Bundesbank) | EONIA y STR (BCE) | **Por comprobar** |
| Sectores (capa 6) | 49 sectores de EE. UU., mensuales desde 1926 (Kenneth French) | Igual | Si |

**Comprobaciones antes de medir (no son medir):** cada serie reconstruida, en los anyos en que coincida con el ETF real
o con la serie del estudio 1, correlacion mensual >= 0,95 (como en el estudio 1). Si alguna falla, se para y se
decide. Se miran solo correlaciones, no rendimientos de ninguna estrategia.

## 4. Las 5 variantes (lista cerrada)

| # | Variante | Regla |
|---|---|---|
| 1 | **H1-M** | Tal cual `docs/diseno-estudio-1.md` 3 (medias de 20/50/100/200 dias, cuartos, mensual, ETF) |
| 2 | **H1-F** | Tal cual (fondos con traspaso, sin oro, ejecucion 6 dias habiles despues, impuestos al final) |
| 3 | **H1-M + capa 2 (volatilidad)** | Peso de cada pieza x min(1, vol. objetivo / vol. de los ultimos 63 dias). Vol. objetivo = mediana de la vol. de 63 dias de esa pieza en los 10 anyos anteriores (solo pasado). Nunca por encima del peso de H1-M |
| 4 | **H1-M + capa 3 (fiscal)** | Igual que H1-M, pero una pieza solo se **reduce** si su senyal baja **2 cuartos o mas**, o llega a 0. Las subidas, como en H1-M |
| 5 | **La mejor de 1-4 + capa 6 (modelo)** | Seccion 5 |

"La mejor de 1-4" = la de mayor Sharpe en 1971-2026; elegirla despues de verla ya esta contado (N = 10).

## 5. Capa 6: el modelo (fijado antes, un solo modelo)

- **Pregunta:** cuando la tendencia dice "dentro", ¿acertara el mes que viene? (no predice el mercado).
- **Datos para aprender:** los 49 sectores, mensuales. Para cada sector y mes con senyal "dentro" (precio por encima
  de su media de 10 meses, la version mensual de la tendencia), etiqueta = 1 si el mes siguiente el sector gana mas que
  las letras del Tesoro, 0 si no.
- **Variables (todas con datos de hasta el mes anterior):** volatilidad de 3 y 12 meses; distancia a la media de 10
  meses en unidades de volatilidad; cuantos de los plazos 1, 3, 6 y 12 meses son positivos; porcentaje de sectores por
  encima de su media; inflacion de EE. UU. de hace 2 meses (12 meses); pendiente de tipos (10 anyos - 3 meses).
- **Modelo:** regresion logistica de scikit-learn con regularizacion fija (C = 1), variables normalizadas con
  ventanas que solo miran atras. Sin probar otros modelos ni otros valores.
- **Entrenamiento:** primero con 1927-1970 (anyos que no se juzgan); despues se reentrena cada enero con todo lo
  anterior (ventana creciente), con 12 meses de separacion entre entrenamiento y uso (purga).
- **Como actua:** cada mes, para cada pieza de la variante base, si la probabilidad es < 0,5, su peso se reduce a la
  mitad (nunca se anyade riesgo).
- **Control de sobreajuste:** probabilidad de sobreajuste (PBO, validacion combinatoria con 8 grupos) < 0,5 y que la
  importancia no dependa de una sola variable (> 40 %).
- **Se queda solo si** la variante 5 pasa todas las condiciones de la seccion 7 **y** mejora el Sharpe de su base.

## 6. Costes, impuestos y referencia

Heredados del estudio 1 (`docs/diseno-estudio-1.md` 4 y 5), sin cambios: ETF 0 € de comision y 0,10 % por lado;
gastos anuales de los ETF reales; fondos al 0,15 %; impuestos al 19 % por lotes, compensacion, arrastre de 4 anyos y
regla de los dos meses (ETF); fondos, todo al final. Referencia: la pieza de bolsa en un fondo indexado mantenido,
impuesto al final. Ejecucion: cierre del dia habil siguiente a la senyal.

## 7. Cuando pasa una variante (todas a la vez)

1. **1971-2026:** TAE >= la de la referencia, o TAE >= la de la referencia - 1 punto **y** caida maxima <= 2/3 de
   la suya.
2. **1990-2026:** lo mismo.
3. **Tipos de mercado:** en los anyos de bolsa a la baja (con inflacion alta y con baja, por separado), media anual
   por encima de la referencia; en los de subida (los dos), como mucho 5 puntos por detras.
4. **No es suerte:** Sharpe deflactado del exceso sobre el monetario >= 0,95 con N = 10 (varianza de los Sharpe de
   las 5 variantes nuevas; si sale menor que la de pura suerte, se usa esa).
5. Solo la variante 5: lo de la seccion 5.

Si pasan varias: la de mayor Sharpe deflactado; si la diferencia es < 0,02, la automatica (ETF) antes que la de fondos.

**Solo informacion (no decide):** cada condicion en 1971-2000 sola (el tramo limpio); 1926-1970 con la bolsa de EE.
UU.; la bolsa fuera de EE. UU. mensual en 1975-1996; anyos por tipo de mercado.

## 8. Antes de que salga mal (pre-mortem)

| Que podria fallar | Prevision |
|---|---|
| Un error al reconstruir una serie decide el resultado | Comprobaciones de la seccion 3 antes de medir; validaciones con datos inventados |
| El bono aproximado no se parece al real | Contraste con VBMFX; si no llega a 0,95, se para |
| Antes de 1997 solo hay bolsa de EE. UU. | Dicho; la mensual de fuera de EE. UU. como informacion |
| Algun tipo de mercado tiene muy pocos anyos (bajada + inflacion alta) | Se informa cuantos; no se cambia la regla despues |
| Pasa por 1971-2000 pero no por 2001-2026 | Lo cubre la condicion 2 (1990-2026) |
| Caidas rapidas con rebote (1987, 2020) | Debilidad conocida; se ve en la informacion por anyos |
| Tentacion de retocar algo tras ver resultados | Prohibido: se mide una vez; cualquier cambio es un estudio nuevo con N + 1 |

## 9. Si pasa / si no pasa

- **Si pasa una:** papel (decision 11) con la IA en sombra (decision 8); dinero real solo con el si del propietario.
- **Si no pasa ninguna:** se escribe por que, y se sigue con el laboratorio de divisas en papel (decision 14.1). No se
  vuelve a medir 1971-2026 con variaciones de estas reglas.

## 10. Pendiente antes de construir

- Comprobar: tipos alemanes diarios, MSCI EAFE con dividendos 1997-2000, oro 1999-2000.
- Aprobacion del propietario de este plan.

## 11. Revision del plan (14/10/2026): agujeros encontrados

Skills: `ml4t-backtest-overfitting`, `ml4t-point-in-time`, `ml4t-non-stationarity`, `ml4t-regime-awareness`. Lo de
esta seccion **manda** sobre lo anterior si se contradicen.

### Correcciones tecnicas (aplicadas)

| # | Agujero | Correccion |
|---|---|---|
| T1 | No se decia como se mide 1990-2026 | Simulacion aparte que empieza el 01/01/1990 con la cuenta nueva (senyales calentadas con datos anteriores) y liquida al final; la referencia, igual |
| T2 | Los impuestos al final deforman los rendimientos de cada anyo | Tipos de mercado con rendimientos anuales **antes de impuestos**; condicion = media de (estrategia - referencia) en los anyos del tipo; 2026 (incompleto) fuera de los tipos, dentro del total |
| T3 | Sobre que se calcula el Sharpe | Rendimientos mensuales sobre el monetario, netos de costes, antes de impuestos; deflactado con asimetria y colas |
| T4 | La capa 2 pide 10 anyos de historia y el oro empieza en 1968 | Ventana creciente hasta 10 anyos, minimo 2; antes, factor 1 |
| T5 | Calentar las medias de 1970 en euros pedia el cambio anterior a 1971 | Marco/dolar diario del Bundesbank desde 1948 (BBEX3.D.USD.DEM.AA.AC.000, comprobado) |
| T6 | El bono a 10 anyos no se parece al indice agregado (VBMFX/EUNA, duracion ~6) | Bono a **7 anyos** (FRED DGS7, diario desde 07/1969, comprobado), duracion calculada cada dia con la rentabilidad |
| T7 | Festivos distintos en Nueva York y Frankfurt | Calendario de la union de dias habiles; en festivo, el ultimo precio |
| T8 | La probabilidad de sobreajuste (PBO) no tiene sentido con un solo modelo | PBO entre {base, base + modelo} con validacion combinatoria de 8 grupos |
| T9 | La pendiente de tipos (10 anyos) no existe antes de 1953 y el modelo aprende con 1927-1970 | Variable eliminada |
| T10 | Anacronismos | ETF antes de 1993, traspasos de fondos antes de 2003 y la ley espanyola de hoy: se simula el vehiculo y las reglas de hoy; dicho en el veredicto |
| T11 | Fuentes | Stooq pide una comprobacion de navegador (no se fuerza); falta la clave del tipo aleman a un dia y el oro 1999-2000 |
| T12 | Tipos de mercado definidos con el anyo entero (despues de pasar) | Correcto solo porque **no** se usan para operar, solo para juzgar (regime-awareness) |

### Decisiones del propietario (una por mensaje)

| # | Cuestion |
|---|---|
| P1 | **Decidido (14/10, opcion A): tramos reales del ahorro de hoy** (territorio comun, Ley 7/2024): 19 % hasta 6.000 €, 21 % hasta 50.000, 23 % hasta 200.000, 27 % hasta 300.000, 30 % por encima; por anyo, sobre la ganancia neta de cada anyo (la referencia, de una vez al final). Fuentes secundarias ([Roams](https://roams.es/finanzas/academia/declaracion-renta/irpf/), BBVA): se contrasta con la AEAT antes de construir |
| P2 | **Decidido (14/10, opcion A): la capa 6 actua solo sobre la pieza de bolsa** (aprende de sectores de bolsa); bonos y oro siguen la variante base sin tocar |
| P3 | Que hacer si un tipo de mercado tiene menos de 3 anyos |
