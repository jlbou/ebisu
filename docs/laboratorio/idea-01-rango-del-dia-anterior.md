# Idea 1 del laboratorio de divisas: rango del dia anterior (borrador, 22/10/2026)

Pertenece al plan `docs/plan-laboratorio-divisas.md` y desarrolla la hipotesis 2 de `docs/hipotesis.md`. **APROBADA por el
propietario el 22/10/2026** (regla, variantes, pares, criterio de paso y parada temprana). **No esta activa:** empieza
cuando se construya el laboratorio. Ninguna cifra de este documento se ha medido.

## 1. La regla (decidida por el propietario, 22/10/2026)

Cada dia, con el rango (maximo y minimo) del dia anterior, se calculan dos niveles:

- **Compra:** una orden en `minimo de ayer + x * (maximo de ayer - minimo de ayer)`.
- **Venta:** el objetivo, en `maximo de ayer - x * (maximo de ayer - minimo de ayer)`.

Reglas de funcionamiento:

1. **Orden automatica** (se ejecuta cuando el precio llega al nivel); no es una revision a una hora fija.
2. Si el precio no llega al nivel de compra, **no hay operacion** y ese dia cuenta **como cero** (no se excluye).
3. Con compra hecha: se vende en el objetivo si el precio llega; si no, **se cierra al final del dia**. Nada pasa la
   noche (sin financiacion nocturna).
4. Solo compras (la version de venta en corto seria otra variante y cuenta aparte).
5. **Sin suposiciones sobre el orden de los precios:** el laboratorio mira hacia delante y guarda precios de 5 minutos
   o por horas, asi que ve el orden real. Solo si algun dia se probase con historia diaria se aplicaria la suposicion
   del peor caso (compra hecha, venta no, cierre al final del dia).

## 2. Variantes (cada una cuenta como prueba)

| Variante | x | Cuenta como |
|---|---|---|
| 1A | 0 % (niveles exactos: minimo y maximo de ayer) | prueba |
| 1B | 20 % (fijada ahora, una sola vez) | prueba |

Pares: **EUR/USD y USD/JPY** (los dos mas liquidos). Total: **2 variantes x 2 pares = 4 pruebas**, mas las del pasado
(H2 en 7 pares, estudio 3 con 27.315 operaciones, fixing), que tambien cuentan para el liston contra la suerte.
No se cuentan como ideas distintas el EUR/USD y su inverso (USD/EUR): es el mismo movimiento.

## 3. Cuando se juzga

**200 operaciones por variante y minimo 3 meses.** Estimacion (no medida): ~9 meses con los dos pares, solo hacia
delante.

## 4. Revision con las skills (22/10/2026)

**ml4t-lookahead-bias:**
- El "dia" de las divisas no tiene cierre natural: hay que fijar la **hora de corte** que define el rango de ayer
  (decidida: seccion 6). Los niveles se calculan **solo con datos anteriores al corte** y las ordenes se colocan despues.
- La orden se considera ejecutada **solo si el precio la atraviesa mas alla del spread**, no si solo la toca (la compra
  entra al precio de venta y la venta al de compra del broker; Yahoo da precios orientativos sin spread).
- Los niveles no pueden usar el rango del propio dia.

**ml4t-transaction-costs:**
- Costes del simulador (sin verificar con cuenta): spread de ~0,7 pips por viaje en EUR/USD, sin comision, sin
  financiacion nocturna (se cierra antes del corte). El de USD/JPY no esta mirado.
- **Margen de seguridad exigido: ganancia bruta / coste >= 2,5x.** Resultados a 1x, 2x y 3x los costes base.
- Con 4x y 1.000 unidades, el coste fijo es pequeno; lo que importa es que el movimiento medio por operacion lo supere.

**ml4t-backtest-overfitting:**
- Contador de pruebas: **N = 4 de esta idea mas las del pasado**; se publica junto al veredicto.
- Regla congelada: ni x, ni los pares, ni la hora de corte se tocan despues de empezar. Cambiar algo es otra idea.
- Las dos variantes comparten los mismos datos: no son independientes, pero cada una cuenta igual.

**ml4t-case-study-development (puertas):**
- Hipotesis falsable y criterio explicitos antes de mirar nada (esta pagina, tras la aprobacion).
- **Criterio de parada temprana (propuesta):** a las 100 operaciones, si el limite superior del intervalo de confianza de
  la media neta por operacion es negativo, se descarta sin esperar a las 200.

## 5. Criterio de paso (APROBADO el 22/10/2026, junto con la parada temprana de la seccion 4)

Pasa solo si se cumplen **las tres**:

1. **Gana despues de costes:** el limite inferior del intervalo de confianza (bootstrap) de la media neta por operacion
   es > 0, con la confianza corregida por el numero de pruebas (Bonferroni: 1 - 0,05 / N).
2. **Aguanta los costes duros:** sigue siendo positiva a 2x los costes base y el margen bruto/coste es >= 2,5x a 1x.
3. **Caida dentro del limite** de la decision 13: < 30 % del capital asignado a 4x.

Si falla una, se descarta. Si pasa: 3 meses mas de confirmacion en papel y las reglas del paso a dinero real del plan.

## 6. Decidido el 22/10/2026

- **Hora de corte del dia:** cierre de Nueva York, **22:00 UTC en invierno y 21:00 UTC en verano**. Define el rango de
  ayer y es la hora antes de la cual se cierra todo (asi no hay financiacion nocturna).
- **Tamanyo:** 1.000 unidades (~4x con 250 €). **Una sola posicion abierta en total** (EUR/USD y USD/JPY dependen del
  dolar y tienden a moverse juntos; dos posiciones serian ~8x, el doble del limite de la decision 13). Si una orden
  llega con otra posicion abierta, no se ejecuta.
- **Minimo de FOREX.com verificado en su web (22/10/2026):** 1.000 unidades (un micro-lote) en EUR/USD; no existe un
  tamanyo menor, asi que no se puede partir la posicion. El minimo de USD/JPY no se ha encontrado aparte.

## 7. Pendiente

- **Verificar con cuenta de FOREX.com:** spread de EUR/USD y de USD/JPY, y el minimo de USD/JPY (panel "Market Info").
