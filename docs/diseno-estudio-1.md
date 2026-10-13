# Diseno del estudio 1: criterio fijado ANTES de medir (APROBADO, 12/10/2026)

**Estado: APROBADO por el propietario el 12/10/2026, por partes (seccion 8). No se ha medido nada.** Desde el commit
que lo aprueba no se cambia nada de lo que aqui se fija; cualquier cambio posterior se anota con fecha y motivo, y
cuenta como una prueba mas.

Viene de: `docs/prd-paso-1.md`, `docs/hipotesis.md`, `docs/estudios/verificaciones-vehiculo.md`,
`docs/estudios/inventario-datos.md`.

## 0. Reglas del estudio

1. **Primero la exploracion; la reserva se mira UNA sola vez**, al final, con lo que haya pasado la exploracion.
2. **Lista cerrada de variantes** (seccion 3): todas se cuentan para el liston contra la suerte, pasen o no.
3. **No se retoca nada** tras ver un resultado: ni plazos, ni dias, ni activos, ni umbrales.
4. Todo en **euros**, neto de **costes e impuestos espanyoles**; el inversor no necesita el dinero en 3 anyos.
5. **Sin apalancamiento.** La version 2x se calcula solo como informacion y nunca se juzga ni se elige.
6. Un juez automatico (`estudios/estudio1/juez.py`) aplica este documento y escribe el veredicto; nadie lo interpreta.

## 1. Periodos (APROBADO por el propietario, 12/10/2026, opcion A)

| Tramo | Fechas | Para que |
|---|---|---|
| Calentamiento | 30/08/2000 - 30/06/2001 | Las medias de 200 dias necesitan historia; no cuenta |
| **Exploracion** | **01/07/2001 - 31/12/2014** (13,5 anyos) | Medir todas las variantes y elegir, con el criterio |
| **Reserva** | **01/01/2015 - 30/09/2026** (11,75 anyos) | Una sola vez, solo con la variante que pase la exploracion |

- Empieza en 2000 porque el oro diario empieza ahi (inventario). Las dos mitades tienen grandes caidas (2001-2003 y
  2008 en la exploracion; 2020 y 2022 en la reserva).
- **Aviso honesto:** todos conocemos por encima lo que paso en esos anyos. Por eso la regla se toma de la literatura y
  de L tal cual, sin ajustar nada a esos anyos.

## 2. Datos (todo en euros)

| Pieza | Serie | Paso a euros |
|---|---|---|
| Bolsa mundial | 60 % VTSMX (EE. UU.) + 40 % VGTSX (resto del mundo), rebalanceado cada mes, con dividendos | Sin cubrir (como VWCE): se aplica el cambio |
| Bonos | VBMFX (bonos de EE. UU., con cupones) | **Cubierto a euros** (como EUNA): rendimiento en dolares + (tipo del euro - tipo del dolar) |
| Oro | Futuro del oro (GC=F) | Sin cubrir (como Xetra-Gold): se aplica el cambio |
| Monetario (refugio) | EONIA hasta 2019 y STR desde entonces (BCE), devengo diario | Ya en euros |
| Cambio euro/dolar | Tipo de referencia del BCE | Fuente oficial (Yahoo solo llega a 2003) |
| Tipo del dolar | Letra a 3 meses de la Reserva Federal (FRED, DTB3; antes ^IRX, ver seccion 9) | Para la cobertura de los bonos |

- **Comprobacion antes de medir** (no es medir): desde que existan, las series largas en euros tienen que parecerse a
  los ETF reales (VWCE o EUNL, EUNA, Xetra-Gold, XEON): correlacion **mensual** >= 0,95 (era diaria: ver seccion 9). Si alguna no llega, se para y se
  decide antes de seguir.
- **Segunda fuente para los precios de Yahoo:** antes de medir, cada serie de Yahoo se contrasta con otra fuente
  independiente (p. ej. Stooq o el valor liquidativo de la gestora) en las fechas en que coincidan. Si difieren mas del
  0,5 % en algun dia sin explicacion (festivo, reparto), se para y se decide antes de seguir.
- Solo dias cerrados. Precio de ejecucion: el **cierre del dia habil siguiente** a la senyal.

## 3. Las hipotesis y sus variantes (lista cerrada)

### H1. Tendencia en tres piezas (la principal) (APROBADA con sus cuatro variantes, 12/10/2026, opcion A)

- **Senyal** (de L y de la literatura: varios plazos juntos): para cada pieza, cuantas de sus medias de **20, 50, 100 y
  200 dias** estan por debajo del precio (0 a 4).
- **Peso** de cada pieza: un tercio x (medias superadas / 4). Lo que no se invierte va al monetario. Ejemplo: bolsa
  con 3 de 4 -> 25 % en bolsa; oro con 4 de 4 -> 33,3 %; bonos con 0 de 4 -> 0 %; el resto, 41,7 % al monetario.
- **Rebalanceo:** solo si el peso de una pieza cambia (evita operar por nada).

| Variante | Frecuencia | Senyal | Vehiculo |
|---|---|---|---|
| **H1-M** (la principal) | mensual (ultimo dia habil) | escalonada (0-4 cuartos) | ETF |
| H1-S | semanal (viernes) | escalonada | ETF |
| H1-MB | mensual | todo o nada (dentro con >= 2 de 4, como el filtro de L) | ETF |
| H1-F | mensual | escalonada | **Fondos con traspaso**: sin oro (mitad bolsa, mitad bonos), ejecucion **6 dias habiles** despues, sin impuestos hasta el final |

### H2. Rango del dia anterior en divisas (la idea de una persona conocida) (APROBADA, 12/10/2026, opcion A)

- **Los 7 pares principales:** EUR/USD, USD/JPY, GBP/USD, USD/CHF, AUD/USD, USD/CAD y NZD/USD. La misma regla en
  todos; **juntos cuentan como UNA variante**. Prohibido quedarse despues solo con los pares que salgan bien.
- **Datos: Dukascopy** (banco suizo regulado; ver seccion 9), velas diarias con **precio de compra y de venta por separado**; el dia,
  de **17:00 a 17:00 de Nueva York**. El coste sale del diferencial real (se compra al precio de venta del mercado y se
  vende al de compra), no de un porcentaje supuesto. Contraste con una segunda fuente antes de medir, como en la
  seccion 2. Los tramos, los de la seccion 1 (la exploracion empieza cuando haya datos de los siete).
- **Regla:** si el precio baja del **minimo de ayer**, compra a ese precio; vende al **maximo de ayer** si se toca ese
  dia, y si no, al cierre. Sin apalancamiento; capital repartido a partes iguales entre los siete, pasado a euros.
- Con velas diarias no se sabe que se toco antes: **si el mismo dia se tocan el minimo y el maximo, se cuenta lo peor**.
- Sin el minimo de 2 $ por orden de IBKR: con 250 € no seria viable de ninguna forma, y se dice. Aqui se mide si la
  idea tiene ventaja.

### H3. Kronos: FUERA de este estudio (12/10/2026, opcion A)

Esta hecho para velas de horas o dias y para ordenar muchos activos; H1 decide una vez al mes entre tres piezas, y en
cripto no acerto. El entorno sigue guardado en Ploutos por si aparece un uso que encaje.

### H4. La IA como filtro

No entra aqui: no se puede probar con la historia (decision 8). Va al papel, despues.

**Total de variantes que cuentan para el liston: N = 5** (H1-M, H1-S, H1-MB, H1-F y H2).

## 4. Costes e impuestos (APROBADO, 12/10/2026, opcion A)

- **ETF (Trading 212):** 0 € de comision; **0,10 % por lado** de diferencial y deslizamiento (conservador); sin cambio
  de divisa (todo cotiza en euros); gasto anual de los ETF reales descontado a diario (bolsa 0,19 %, bonos 0,10 %,
  oro 0,25 %, monetario 0,10 %), menos lo que ya llevan las series largas (se resta la diferencia).
- **Fondos:** 0 € por operar; gasto anual 0,15 %; **sin oro**.
- **Impuestos (Espanya, 250 €: tramo del 19 %):**
  - ETF: cada venta con ganancia tributa el anyo en que se hace; las perdidas compensan ganancias del mismo anyo y se
    arrastran 4 anyos; **regla de los dos meses**: una perdida no cuenta si se recompra la misma pieza en 2 meses.
  - Fondos: nada hasta el final.
  - **Al final de cada tramo se liquida todo** y se paga lo pendiente: se compara lo que quedaria en el bolsillo.

## 5. La referencia (APROBADA, 12/10/2026, opcion A)

- **Principal (decision 1):** la bolsa mundial de la seccion 2 en un **fondo indexado mantenido**, comprado el primer
  dia del tramo, sin operar, con gasto anual del 0,15 % y **todo el impuesto al final**.
- **Informativas** (no deciden): las tres piezas a partes iguales rebalanceadas una vez al anyo; y la bolsa mundial
  mantenida en un ETF.

## 6. Cuando pasa (APROBADO, 12/10/2026, opcion A)

En cada tramo se mide, sobre lo que quedaria en el bolsillo: **rendimiento anual (TAE)**, **caida maxima** y
**Sharpe** (con el monetario como tipo sin riesgo).

**Exploracion: una variante pasa si cumple las tres:**

1. **Gana a la referencia, o casi la iguala con claramente menos caida:** TAE >= la de la referencia, **o** TAE >= la
   de la referencia **- 1 punto** **y** caida maxima <= **2/3** de la de la referencia.
2. **No pierde dinero** en el tramo (TAE > 0).
3. **No es suerte:** Sharpe deflactado >= **0,95** con N = 5.

H2 pasa si ademas, **juntando las operaciones de los siete pares**, el **rendimiento medio por operacion, neto, tiene
el IC del 90 % por encima de 0**, **y** ese rendimiento medio es positivo en **al menos 5 de los 7 pares**.

**Si pasa mas de una, va a la reserva la de mayor Sharpe deflactado** (solo una). Si no pasa ninguna, el estudio
termina ahi: **la conclusion es el indexado mantenido** (decision 7), y la reserva queda sin tocar.

**Reserva: pasa si cumple 1 y 2** (el deflactado ya se exigio). Si pasa, se va al papel hacia adelante; si no, se
acaba igual: indexado mantenido.

**Informacion que no decide:** la version 2x de cada variante; los anyos uno a uno; las operaciones; el peso medio.

## 7. Orden de trabajo (cada paso, con su commit)

1. ~~Aprobar este documento (por partes) y subirlo~~: hecho (12/10).
2. Bajar las fuentes oficiales (BCE: euro/dolar, EONIA, STR), las divisas de Dukascopy y la segunda fuente, y montar
   las series en euros.
3. Las comprobaciones de la seccion 2 (parecido con los ETF reales y segunda fuente). Sin mirar rendimientos.
4. Escribir el simulador y el juez, y **validarlos antes de medir**: con pesos fijos tiene que dar exactamente comprar
   y mantener (como en Ploutos).
5. Medir la exploracion. Veredicto del juez.
6. Si alguna pasa: la reserva, una vez. Veredicto.

## 8. Decisiones del propietario para aprobar este borrador

1. ~~Los periodos (seccion 1)~~: **aprobados** (12/10, opcion A).
2. ~~La regla de H1 y sus cuatro variantes (seccion 3)~~: **aprobadas** (12/10, opcion A).
3. ~~Costes e impuestos (seccion 4) y la referencia (seccion 5)~~: **aprobados** (12/10, opcion A).
4. ~~Cuando pasa: los umbrales (seccion 6)~~: **aprobados** (12/10, opcion A).
5. ~~H2 y H3 (seccion 3)~~: **aprobado** (12/10, opcion A): H2 con los 7 pares principales como una variante y datos de
   Dukascopy; segunda fuente para todo lo de Yahoo; Kronos fuera.

## 9. Cambios despues de aprobar (cada uno con fecha y motivo; ninguno toca reglas, variantes ni umbrales)

**12/10/2026. Arbitraje de las fuentes (opcion A del propietario), antes de medir nada.**

- **El contraste encontro diferencias** entre Yahoo y Nasdaq (`estudios/estudio1/segunda_fuente.py`): en VGTSX
  (177 dias) y VBMFX (82 dias), casi todas de 05/2002 a 01/2003 (hasta un 23 %); dias sueltos en VTSMX (7) y GLD (1).
- **Tercera fuente, oficial: los informes de Vanguard en la SEC** (valor liquidativo al cierre de cada periodo):

  | Fondo | Fecha | Oficial (SEC) | Yahoo | Nasdaq |
  |---|---|---|---|---|
  | VGTSX | 31/10/2002 | 7,79 | 7,79 | 7,76 |
  | VGTSX | 31/10/2001 | 8,99 | 9,00 | 9,00 |
  | VGTSX | 31/12/2000 | 11,83 | 11,83 | - |
  | VBMFX | 30/06/2002 | 10,13 | 10,13 | 10,14 |
  | VBMFX | 31/12/2001 | 10,15 | 10,14 | 10,14 |
  | VBMFX | 31/12/2000 | 9,96 | 9,96 | 9,96 |

  Fuentes: [informe anual de Vanguard International Equity Index Funds a 31/10/2002](https://www.sec.gov/Archives/edgar/data/857489/000093247103000009/intrnlstockindex.txt)
  y [semestral de Vanguard Bond Index Funds a 30/06/2002](https://www.sec.gov/Archives/edgar/data/794105/000093247102000763/bonds2002ascii.txt).
- **Decision: se usa Yahoo**, que coincide con lo oficial (a un centimo como mucho) en los seis puntos; Nasdaq es la que
  falla en 2002 (no es un simple desfase de fechas). Los dias sueltos de VTSMX y GLD quedan anotados: con una decision
  al mes, su efecto es menor.
- **El tipo del dolar pasa de ^IRX (Yahoo) a DTB3 de la Reserva Federal (FRED)**, la serie oficial de la letra a 3
  meses: las dos difieren hasta 0,51 puntos en 261 dias porque no son exactamente el mismo indice.
- Stooq no sirvio como segunda fuente: pide una verificacion de navegador, y no se salta.

**12/10/2026. La comprobacion de parecido pasa de diaria a mensual (opcion A del propietario), antes de medir nada.**

- **Lo que salio** (`estudios/estudio1/montar_series.py`, solo correlaciones): diaria 0,30-0,83 en las cinco
  comparaciones; semanal 0,87-0,94; **mensual 0,96-0,99**, salvo los bonos (**0,943**).
- **Por que la diaria no sirve:** las series largas cierran en Nueva York (22:00 en Espanya), los ETF reales en
  Frankfurt (17:30) y el cambio del BCE es de las 14:15: un dia se compara con trozos de dos. A la misma hora, la bolsa
  casa a 0,98-0,99 (60/40 frente a VT y ACWI, en dolares). En el monetario, el ruido diario de compraventa del ETF
  sobre un rendimiento casi plano hace la diaria inutil.
- **Decision:** la comprobacion es **mensual >= 0,95**, el horizonte en que decide la estrategia.
- **Bonos (0,943): se aceptan como limitacion conocida.** La serie larga son bonos de EE. UU. cubiertos a euros; el ETF
  real, bonos de todo el mundo cubiertos a euros: indices distintos, y no hay serie gratuita de bonos mundiales antes
  de 2013. Se decidio despues de ver el numero, y se dice: es una comprobacion de datos, no de la estrategia.
- **Error del borrador:** la comparacion diaria debio preverse inservible por las horas de cierre.

**12/10/2026. La fuente de H2 pasa de Dukascopy a OANDA (opcion A del propietario), antes de medir nada.**

- **Motivo:** el servidor de Dukascopy tarda ~1 minuto por fichero (y corta a menudo); los ~4.000 ficheros de velas
  de 1 hora de los siete pares tardarian ~3 dias. Los primeros meses de 2003 venian vacios.
- **OANDA** (broker regulado), cuenta de **practica** sin dinero: su API da velas **diarias ya cortadas a las 17:00 de
  Nueva York**, con **compra y venta por separado**. Cumple la definicion de H2 sin cambiarla.
  (`estudios/estudio1/bajar_oanda.py`; el token lo pone el propietario en el `.env`.)
- **Por verificar al bajar:** desde que anyo hay datos de cada par. Como ya decia H2, la exploracion empieza cuando
  haya datos de los siete. Contraste con una segunda fuente antes de medir, como en la seccion 2.

**12/10/2026. Se deshace el cambio a OANDA: H2 vuelve a Dukascopy (opcion A del propietario), antes de medir nada.**

- **Motivo:** desde 2023 los clientes de la UE de OANDA pasan a OANDA TMS Brokers (Polonia), que **no tiene la API
  v20**; para Espanya solo se ofrece la cuenta de acciones. Se debio verificar antes de proponerlo.
- **Dukascopy, velas de 1 hora, despacio:** ~3 dias de descarga en segundo plano, que se reanuda donde lo dejo. Cumple
  H2 tal cual (dia de 17:00 a 17:00 de Nueva York, compra y venta reales). Se borra `bajar_oanda.py` y sus variables.

**13/10/2026. Contraste de las divisas de H2 con el BCE (antes de medir nada): pasa.**

- Bajada de Dukascopy completa el 13/10 a las 05:30 (3.990 ficheros, 7 pares; los 4 primeros desde 05/2003, AUD, CAD
  y NZD desde 08/2003). `estudios/estudio1/contraste_h2.py`: el tipo de referencia del BCE cae dentro del rango del
  dia de Dukascopy el **99,9-100 % de los dias** en los siete pares.
- **Un solo dia fuera mas del 0,5 %: AUD/USD el 06/05/2020 (0,84 %). Explicado: el fallo es del BCE**, no de
  Dukascopy. Ese dia el BCE da 1,7046 dolares australianos por euro (1,6825 el dia antes y 1,6704 el despues); la
  Reserva Federal (FRED, DEXUSAL) da 0,6414 dolares por dolar australiano, **dentro** del rango de Dukascopy
  (0,6393-0,6453). No se para: se sigue con Dukascopy tal cual.
