# Diseno del estudio 1: criterio fijado ANTES de medir (BORRADOR, 12/10/2026)

**Estado: BORRADOR, sin aprobar. No se ha medido nada.** Cuando el propietario lo apruebe, se sube a git y desde ese
commit no se cambia nada de lo que aqui se fija; cualquier cambio posterior se anota con fecha y motivo, y cuenta como
una prueba mas.

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
| Tipo del dolar | Letra a 13 semanas (^IRX) | Para la cobertura de los bonos |

- **Comprobacion antes de medir** (no es medir): desde que existan, las series largas en euros tienen que parecerse a
  los ETF reales (VWCE o EUNL, EUNA, Xetra-Gold, XEON): correlacion diaria >= 0,95. Si alguna no llega, se para y se
  decide antes de seguir.
- Solo dias cerrados. Precio de ejecucion: el **cierre del dia habil siguiente** a la senyal.

## 3. Las hipotesis y sus variantes (lista cerrada)

### H1. Tendencia en tres piezas (la principal)

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

### H2. Rango del dia anterior en divisas (la idea de una persona conocida)

- USD/CAD diario (OHLC de Yahoo). Si el precio baja del **minimo de ayer**, compra a ese precio; vende al **maximo de
  ayer** si se toca ese dia, y si no, al cierre. Sin apalancamiento.
- Con velas diarias no se sabe que se toco antes: **si el mismo dia se tocan el minimo y el maximo, se cuenta lo peor**.
- Coste: un diferencial de 0,02 % por lado (sin el minimo de 2 $ de IBKR: con 250 € no seria viable de ninguna forma,
  y se dice).
- Una sola variante (H2).

### H3. Kronos

**Propuesta: no se prueba en este estudio.** Esta hecho para velas de horas o dias y para ordenar muchos activos; H1
decide una vez al mes entre tres piezas. Sacarlo de la lista es decision del propietario (decision 7).

### H4. La IA como filtro

No entra aqui: no se puede probar con la historia (decision 8). Va al papel, despues.

**Total de variantes que cuentan para el liston: N = 5** (H1-M, H1-S, H1-MB, H1-F y H2).

## 4. Costes e impuestos

- **ETF (Trading 212):** 0 € de comision; **0,10 % por lado** de diferencial y deslizamiento (conservador); sin cambio
  de divisa (todo cotiza en euros); gasto anual de los ETF reales descontado a diario (bolsa 0,19 %, bonos 0,10 %,
  oro 0,25 %, monetario 0,10 %), menos lo que ya llevan las series largas (se resta la diferencia).
- **Fondos:** 0 € por operar; gasto anual 0,15 %; **sin oro**.
- **Impuestos (Espanya, 250 €: tramo del 19 %):**
  - ETF: cada venta con ganancia tributa el anyo en que se hace; las perdidas compensan ganancias del mismo anyo y se
    arrastran 4 anyos; **regla de los dos meses**: una perdida no cuenta si se recompra la misma pieza en 2 meses.
  - Fondos: nada hasta el final.
  - **Al final de cada tramo se liquida todo** y se paga lo pendiente: se compara lo que quedaria en el bolsillo.

## 5. La referencia

- **Principal (decision 1):** la bolsa mundial de la seccion 2 en un **fondo indexado mantenido**, comprado el primer
  dia del tramo, sin operar, con gasto anual del 0,15 % y **todo el impuesto al final**.
- **Informativas** (no deciden): las tres piezas a partes iguales rebalanceadas una vez al anyo; y la bolsa mundial
  mantenida en un ETF.

## 6. Cuando pasa

En cada tramo se mide, sobre lo que quedaria en el bolsillo: **rendimiento anual (TAE)**, **caida maxima** y
**Sharpe** (con el monetario como tipo sin riesgo).

**Exploracion: una variante pasa si cumple las tres:**

1. **Gana a la referencia, o casi la iguala con claramente menos caida:** TAE >= la de la referencia, **o** TAE >= la
   de la referencia **- 1 punto** **y** caida maxima <= **2/3** de la de la referencia.
2. **No pierde dinero** en el tramo (TAE > 0).
3. **No es suerte:** Sharpe deflactado >= **0,95** con N = 5.

H2 pasa si ademas el **rendimiento medio por operacion, neto, tiene el IC del 90 % por encima de 0**.

**Si pasa mas de una, va a la reserva la de mayor Sharpe deflactado** (solo una). Si no pasa ninguna, el estudio
termina ahi: **la conclusion es el indexado mantenido** (decision 7), y la reserva queda sin tocar.

**Reserva: pasa si cumple 1 y 2** (el deflactado ya se exigio). Si pasa, se va al papel hacia adelante; si no, se
acaba igual: indexado mantenido.

**Informacion que no decide:** la version 2x de cada variante; los anyos uno a uno; las operaciones; el peso medio.

## 7. Orden de trabajo (cada paso, con su commit)

1. Aprobar este documento (por partes) y subirlo.
2. Bajar las fuentes oficiales (BCE: euro/dolar, EONIA, STR) y montar las series en euros.
3. La comprobacion de la seccion 2 (parecido con los ETF reales). Sin mirar rendimientos.
4. Escribir el simulador y el juez, y **validarlos antes de medir**: con pesos fijos tiene que dar exactamente comprar
   y mantener (como en Ploutos).
5. Medir la exploracion. Veredicto del juez.
6. Si alguna pasa: la reserva, una vez. Veredicto.

## 8. Decisiones del propietario para aprobar este borrador

1. ~~Los periodos (seccion 1)~~: **aprobados** (12/10, opcion A).
2. La regla de H1 y sus cuatro variantes (seccion 3).
3. Costes e impuestos (seccion 4) y la referencia (seccion 5).
4. Cuando pasa: los umbrales (seccion 6).
5. H2 tal cual y H3 fuera (seccion 3).
