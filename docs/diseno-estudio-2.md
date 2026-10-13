# Diseno del estudio 2: criterio fijado ANTES de medir (APROBADO, 13/10/2026)

**Estado: APROBADO por el propietario el 13/10/2026, por partes. No se ha medido nada.** Desde este commit no se
cambia nada de lo fijado; cualquier cambio posterior se anota con fecha y motivo. Viene de `docs/estudios/estudio1-exploracion.md`
(no paso ninguna) y de `docs/estudios/recerca-mejoras.md` (que mejoras tienen evidencia).

## 0. La idea y las reglas

- **Una sola estrategia nueva, decidida con la literatura y no con los resultados del estudio 1:** seguir la tendencia
  con **mas activos poco correlacionados** y **pesos segun el riesgo**, mensual y sin apalancamiento.
- **Se prueba UNA vez, directamente en la reserva** (2015-2026, que nadie ha mirado). Al ser una sola prueba, no hay
  correccion por muchas variantes.
- Nada se retoca despues de ver el resultado. Si no pasa, Ebisu se cierra con el indexado mantenido.

## 0b. Dos candidatas en paralelo (aprobado por el propietario, 13/10/2026, opcion B)

- **E2:** la estrategia nueva de este documento (9 activos, pesos por riesgo).
- **H1-F:** la mejor del estudio 1 (fondos con traspaso, bolsa y bonos sin oro, ejecucion 6 dias habiles despues,
  impuestos al final), **tal cual** esta definida en `docs/diseno-estudio-1.md`, con sus datos y su referencia; su
  reserva tampoco la ha mirado nadie.
- **Liston corregido por ser dos:** cada una necesita la condicion 3 con **>= 0,95** (en vez de 0,90): asi la
  probabilidad de que al menos una pase por pura suerte sigue en el 10 %.
- **Si pasan las dos, van las dos al papel en paralelo** y el propietario decide con los resultados del papel. Si pasa
  una, esa. Si ninguna, Ebisu se cierra con el indexado mantenido.

## 1. Los 9 activos (aprobado por el propietario, 13/10/2026)

El propietario eligio 9 (frente a 5 o 13: ver la recerca). Cada uno con su ETF en euros (vehiculo) y la serie de
precios que se usa para el estudio (historia desde 2013 como mucho, para calentar las medias de 200 dias en 2014).

| # | Activo | ETF (vehiculo) | ISIN | Serie del estudio (Yahoo) |
|---|---|---|---|---|
| 1 | Bolsa EE. UU. | iShares Core S&P 500 (Acc) | IE00B5BMR087 | SXR8.DE (2010) |
| 2 | Bolsa Europa | iShares Core MSCI Europe (Acc) | IE00B4K48X80 | SMEA.MI (2010) |
| 3 | Bolsa emergente | iShares MSCI EM (Acc) | IE00B4L5YC18 | EUNM.DE (2009) |
| 4 | Bonos del Estado de la zona euro | iShares Core EUR Govt Bond | IE00B4WXJJ64 | EUNH.DE (2009) |
| 5 | Bonos corporativos en euros | iShares Core EUR Corp Bond | IE00B3F81R35 | EUN5.DE (2009) |
| 6 | Bonos del Estado de EE. UU. 7-10 anyos (sin cubrir el dolar) | iShares USD Treasury Bond 7-10yr | IE00B1FZS798 | IUSM.DE (2009) |
| 7 | Oro | Invesco Physical Gold (Milan) | IE00B579F325 | 4GLD.DE, Xetra-Gold (2009) |
| 8 | Materias primas | WisdomTree Broad Commodities | GB00B15KY989 | AIGC.MI (2008) |
| 9 | Inmobiliario mundial | iShares Developed Markets Property Yield | IE00B1FZS350 | IQQ6.DE (2008) |

- El lugar 6 iba a ser bonos mundiales cubiertos (EUNA), pero su ETF solo existe desde 2017: el propietario eligio
  los del Estado de EE. UU. (opcion A, 13/10), que suelen ir al reves de la bolsa en las crisis.
- Los ISIN se comprueban en Trading 212 (busqueda por ISIN en la app) antes de aprobar el criterio. Las fechas son las
  de Yahoo, solo fechas (no se ha mirado ningun rendimiento).
- Las series de Yahoo se contrastan con una segunda fuente antes de medir, como en el estudio 1.

**Comprobado en Trading 212 (13/10, busqueda por ISIN del propietario; sin comprar nada):** los 9 estan, en euros.

| # | Linea en Trading 212 (EUR) |
|---|---|
| 1 | SXR8, Xetra |
| 2 | EUNK, Xetra |
| 3 | IEMA, Amsterdam |
| 4 | EUNH, Xetra |
| 5 | IEAC, Londres (cotiza en EUR) |
| 6 | BTMA, Amsterdam |
| 7 | SGLD, Milan |
| 8 | AIGCP, Paris |
| 9 | IWDP, Amsterdam |

Junto a varios salen lineas "5X - CFD": nunca. Las fracciones de cada uno, por comprobar si se llega a operar.

## 2. Como se reparten los pesos (aprobado por el propietario, 13/10/2026, opcion A: segun el riesgo)

- **Senyal (igual que H1):** para cada activo, cuantas de sus medias de 20, 50, 100 y 200 dias estan por debajo del
  precio, `n` de 0 a 4. Sobre la serie en euros.
- **Parte de cada activo, inversa a su riesgo:** `p_i = (1 / s_i) / suma_j (1 / s_j)`, donde `s_i` es la desviacion
  tipica de sus rendimientos diarios en euros de los **ultimos 63 dias habiles** (~3 meses). Las partes suman 1.
- **Peso objetivo:** `w_i = p_i x n_i / 4`. Lo que no se invierte va al monetario.
- **Sin apalancamiento:** la suma de los pesos nunca pasa del 100 % (por construccion, como mucho 1).
- **Apalancamiento:** no ahora (regla dura, decision 5). Como en el estudio 1, se calcula una version 2x **solo como
  informacion**. El propietario no lo descarta para el futuro: se replantearia solo por la via de la decision 5 (con
  resultados reales sin apalancamiento que pasen y mas capital) y nunca para rescatar un resultado justo.

## 3. Cuando se mueve cada pieza (aprobado por el propietario, 13/10/2026, opcion A)

- Revision **mensual**: senyal el ultimo dia habil del mes, ejecucion al cierre del dia habil siguiente (como H1-M).
- Una pieza **solo se toca si su peso objetivo se aleja mas de 2 puntos** del que tiene (p. ej. con un 10 %, no se
  toca si el objetivo es 10,8 %; si es 13 %, si).
- **Excepcion para que la banda no estropee la senyal:** si el objetivo es **0** (salir del todo) o la pieza esta a 0
  y el objetivo no (entrar), se ejecuta siempre, aunque la diferencia sea menor de 2 puntos.
- Al tocar una pieza se lleva exactamente a su objetivo; el monetario absorbe la diferencia (sin apalancamiento).

## 4. Cuando pasa (aprobado por el propietario, 13/10/2026, opcion A)

Tramo: **reserva, 01/01/2015 - 30/09/2026** (las medias y la volatilidad se calientan con datos de 2014). Una sola
medicion. Pasa si cumple las tres, sobre lo que quedaria en el bolsillo tras venderlo todo y pagar lo pendiente:

1. **Gana a la referencia, o casi la iguala con claramente menos caida:** TAE >= la de la referencia, o TAE >= la de
   la referencia - 1 punto y caida maxima <= 2/3 de la de la referencia (decision 1, como en el estudio 1).
2. **No pierde dinero** en el tramo (TAE > 0).
3. **El exceso sobre el monetario no es cero con confianza suficiente:** Sharpe probabilistico contra 0 (Bailey y
   Lopez de Prado, con la asimetria y la curtosis reales) **>= 0,95 para cada una de las dos candidatas** (era 0,90
   con una sola; ver 0b). Se baja del 95 % al 90 % porque con ~12 decisiones al anyo y ~12 anyos el test tiene poca potencia (ver
   `docs/estudios/recerca-mejoras.md` 2); fijado antes de medir.

Si pasa: papel hacia adelante (`docs/decisiones/11-papel.md`: mensual, 6 meses). Si no: **Ebisu se cierra con el
indexado mantenido**, sin mas intentos.

## 5. Costes, impuestos y referencia (heredados del estudio 1; aprobados con la seccion 4)

- **Series de precios:** las de los propios ETF (o la misma cartera en otra bolsa), con los repartos reinvertidos
  (precio ajustado). El gasto anual de cada ETF ya va dentro del precio: no se resta otra vez. El oro usa Xetra-Gold
  (gasto ~0,36 %/anyo frente al 0,12 % de SGLD: conservador).
- **Repartos de los ETF de distribucion** (4, 5, 6 y 9): tributan al 19 % el anyo en que se cobran y se reinvierte el
  resto.
- **Costes:** 0,10 % por lado en cada compra o venta (tambien al entrar y salir del monetario).
- **Impuestos (19 %):** por lotes, compensacion anual, perdidas arrastradas 4 anyos, regla de los dos meses; al final
  del tramo se vende todo y se paga lo pendiente.
- **Monetario:** EONIA y STR del BCE, como en el estudio 1 (vehiculo: XEON).
- **Referencia:** el indexado mundial mantenido (MSCI World en euros, EUNL/IWDA), comprado el primer dia, sin operar,
  con todo el impuesto al final.
- **Informacion que no decide:** la version 2x, los anyos uno a uno, las operaciones, los pesos medios.

## 6. Orden de trabajo (cada paso, con su commit; sin mirar ningun rendimiento hasta el paso 5)

1. Aprobar este documento y subirlo.
2. Bajar las 9 series (y la referencia) y contrastarlas con una segunda fuente: el valor liquidativo publicado por cada
   gestora (iShares, Invesco, WisdomTree) en las fechas en que coincidan. Mas de un 0,5 % de diferencia sin
   explicacion en algun dia: se para y se decide.
3. Adaptar el simulador (9 activos, pesos por riesgo, banda de 2 puntos, repartos) y **validarlo con datos inventados**
   (con pesos fijos tiene que dar comprar y mantener).
4. Adaptar el juez (condiciones 1-3) y validarlo con datos inventados.
5. Medir la reserva **una vez** (`--confirmo`), las dos candidatas a la vez. Veredicto del juez, sin retoques.
