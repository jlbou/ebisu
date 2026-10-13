# Plan del estudio 3 (divisas): todo antes de construir nada (13/10/2026, BORRADOR para el propietario)

Pedido por el propietario: "abans de construir res, vull tenir segur que no ens deixem res". Se revisa cada capa con
las skills de `ml4t/skills` (instaladas solo en local: data-leakage, backtest-overfitting, purging-embargo, cpcv,
walk-forward-cv, deflated-sharpe, triple-barrier, meta-labels, horizon-design, feature-validation, feature-selection,
regime-features, regime-awareness, non-stationarity, drift-detection, cost-model, position-sizing, risk-metrics,
sensitivity-analysis, model-validation, shap-analysis, stationarity-tests) y la de analisis estadistico. **Nada medido.
No se construye nada hasta que el propietario apruebe este plan.**

Viene de: `docs/estudios/recerca-divisas.md`, `docs/estudios/estudio3-opciones.md`,
`docs/estudios/verificaciones-vehiculo.md` 7 y `docs/decisiones/13-apalancamiento-divisas.md`.

## 1. Lo decidido hasta ahora

- Divisas; 5 capas (senyal, reglas, modelo, proteccion, IA); la de solo reglas como control.
- ~4x (el minimo para 1.000 unidades con 250 €), una posicion abierta, calendario de eventos; liston de riesgo M.
- Exploracion y reserva con **pares no tratados**; los 7 principales (ya vistos) solo para disenyar.

## 2. Lo que las skills cambian del plan (hallazgos)

1. **El tamanyo no se puede graduar.** Con 250 € y un minimo de 1.000 unidades, cada operacion es 0 o 1.000 unidades
   (2.000 serian ~8x, fuera de la decision 13). La capa 3 **no puede "poner menos cuando duda"**: solo puede filtrar
   (entrar o no). Lo mismo para escalar por regimen.
2. **Regimenes: escalar, no encender/apagar** (regime-awareness). Con el tamanyo fijo no se puede escalar: los
   regimenes (tendencia, volatilidad, huida del riesgo) entran como **variables del modelo**, no como vetos; el veto
   binario queda solo para lo **programado y conocido de antemano** (calendario), que no es una prediccion.
3. **No se le puede pedir al modelo que cree una ventaja que la senyal no tiene** (meta-labels: la senyal base debe
   tener algo estable). La senyal base (comprar en el minimo de ayer) perdia en todas las versiones. Por eso el
   **diagnostico** (seccion 4) es una puerta: si las perdidas no se concentran en situaciones reconocibles, se para.
4. **Las miradas informales cuentan como pruebas** (backtest-overfitting, deflated-sharpe). Ya hemos mirado, en los 7
   principales: H2 diaria, H2 por horas, objetivo en el maximo sin stop y objetivo en la mitad sin stop. Se cuentan.
5. **Barreras adaptadas a la volatilidad** (triple-barrier): el stop y el objetivo en multiplos del rango medio, no en
   porcentajes fijos. El objetivo del propietario (la mitad del rango de ayer) ya se adapta solo.
6. **Si se tocan dos barreras en la misma hora, cuenta el stop** (triple-barrier): la regla prudente, fijada antes.
7. **Operaciones solapadas no son independientes** (triple-barrier, purging-embargo): el numero efectivo es ~N/H (H =
   duracion maxima de la operacion). Validacion con purga de H dias y embargo.
8. **Ganancia por operacion >= 2,5 veces el coste** (horizon-design), con los costes reales del CFD.
9. **Probabilidad de sobreajuste (PBO) < 0,5** con validacion combinatoria purgada (cpcv), ademas del Sharpe
   deflactado (que ya usamos).
10. **Robustez de parametros** (sensitivity-analysis): mas del 60 % de la rejilla con Sharpe > 0 y sin precipicios; el
    optimo no puede estar en el borde de la rejilla.
11. **El modelo no puede depender de una sola variable** (> 40 % de la importancia, model-validation/shap-analysis).
12. **Variables estacionarias y sin mirar el futuro** (regime-features, non-stationarity, data-leakage): todas
    retrasadas un dia, normalizadas con ventanas moviles, y todo lo que "aprende" se ajusta solo con entrenamiento.
13. **Riesgo, no solo Sharpe** (risk-metrics): caida maxima y su duracion, Sortino, Calmar, CVaR, ademas del liston M.
14. **Cuando reentrenar, fijado antes** (drift-detection): umbrales predefinidos, no despues de perder.

## 3. Datos

| Pieza | Plan | Riesgo / comprobacion |
|---|---|---|
| Pares nuevos | Dukascopy, velas de 1 hora, compra y venta | Fecha de inicio de cada par (comprobando); huecos; contraste con el BCE en los cruces del euro |
| Tramos | Exploracion: desde el inicio de cada par hasta 2014; reserva: 2015-2026, una vez | Si un par empieza tarde, tiene poca exploracion: minimo por decidir |
| Pares principales | Solo para disenyar y para el diagnostico | Ya vistos: nada de lo que digan es una prueba |
| Apalancamiento por par | 1.000 unidades de la divisa base: EUR ~1.000 €, GBP ~1.150 €, USD ~920 € | Con base GBP pasa de 4x: **decidir el maximo por par** |
| Calendario de eventos | Decisiones de bancos centrales (Fed, BCE, BoE, BoJ, SNB, RBA, BoC, RBNZ, Norges, Riksbank), empleo de EE. UU., referendums y elecciones, 2003-2026 | **Sin comprobar que existan calendarios historicos completos y gratuitos** |
| Tipos de interes por divisa | Para los intereses de cada noche del CFD | Fuentes oficiales por divisa (sin comprobar); el recargo del broker, de su web |

## 4. Diagnostico (puerta 1, antes de disenyar reglas o modelo)

Con los 7 principales (ya vistos), compras en el minimo de ayer con las tres barreras y ~4x: clasificar las perdidas
grandes por escenario (los 6 de `recerca-divisas.md`) y de cada peor perdida, que pasaba ese dia. **Pasa la
puerta** si una parte grande de la perdida total se concentra en escenarios que se pueden reconocer **antes** de
comprar (umbral por decidir). Si no, se para aqui y se le explica al propietario.

## 5. Las capas, una a una

| Capa | Que hace | Decisiones pendientes | Como no enganyarnos |
|---|---|---|---|
| 1. Senyal | Comprar cuando el ask toca el minimo de ayer | Si se exige que lo cruce (p. ej. 1 pip) para asegurar que se habria llenado la orden | La orden limite no siempre se llena al tocar: regla prudente |
| Una sola posicion | Si saltan varios pares, cual | La primera en el tiempo (por horas) o la de mas probabilidad del modelo | Regla fijada antes |
| 2. Reglas (veto) | Solo eventos programados: no se compra ese dia ni el anterior | Que eventos, cuantos dias alrededor | Calendario con fechas publicadas antes, no reconstruidas |
| 3. Modelo | Probabilidad de que la compra salga bien; entra solo por encima de un umbral | Regresion logistica o arboles (dependencia: scikit-learn); variables; umbral | Validacion anidada y purgada, CPCV, PBO, SHAP, prueba con etiquetas al azar |
| 4. Proteccion | Objetivo (mitad del rango de ayer), stop (multiplo del rango medio), limite de tiempo, freno mensual | Los cuatro valores | Rejilla pequenya fijada antes y robustez > 60 % |
| 5. IA | Lee noticias; solo puede frenar | Que lee y cuando | No se puede probar con la historia: solo en papel, en sombra |

## 6. Costes y fiscalidad reales

- Diferencial real (compra y venta de Dukascopy) **mas el recargo del broker de CFD** (sin comprobar; el de su web).
- Intereses de cada noche: diferencia de tipos + recargo del broker, x ~4.
- Ejecucion: stop en un salto = primer precio disponible despues del salto (peor que el stop).
- Comparar siempre con y sin costes (cost-model).
- Fiscalidad de los CFD en Espanya: **sin comprobar** (probablemente ganancia patrimonial al 19 %).

## 7. Cuando pasa (todas, fijadas antes de medir la reserva)

1. Gana dinero neto (TAE > 0 tras costes, intereses e impuestos).
2. **Objetivo de la decision 1** (ganar al indexado mantenido, o igualarlo con mucha menos caida): **decidir si se
   aplica igual**: con ~4x y 250 € el riesgo es otro.
3. No es suerte: Sharpe deflactado >= 0,95 contando **todas** las pruebas (tambien las informales del punto 2.4), y
   PBO < 0,5.
4. Liston de riesgo M (decision 13).
5. Robustez y estabilidad: > 60 % de la rejilla con Sharpe > 0; la mejora sale en la mayoria de pares, no solo en el
   total; perdida de rendimiento fuera de muestra < 30 % (y sospecha si es < 5 %: fuga).

Despues: papel (decision 11: para una estrategia diaria, duracion por decidir) y solo entonces dinero real.

## 8. Pre-mortem: "ha fallado; por que?"

| Por que fallo | Como se evita |
|---|---|
| Usaba datos del futuro sin querer | Prueba automatica: desplazar cada variable un dia mas no puede mejorar el resultado; ajuste solo con entrenamiento |
| Probamos tantas combinaciones que una salio por suerte | Contar todas, deflactado, PBO, reserva una sola vez |
| La senyal base no tenia nada | Puerta del diagnostico |
| Los costes reales eran mayores (recargo, intereses, saltos) | Costes del broker de su web, caso prudente, comparar con y sin costes |
| La orden no se llenaba al tocar el minimo | Exigir cruzar el nivel |
| Datos malos en los cruces | Contraste con el BCE; huecos marcados |
| El calendario historico estaba incompleto | Verificar fuentes; si no hay, el veto no se puede probar |
| El mercado cambio despues de 2026 | Deteccion de deriva, freno mensual, papel |
| Una sorpresa (franco suizo) se lleva la cuenta | Liston M (estres), una posicion, stop; el peor caso son 250 € |
| El precio del CFD no es el de Dukascopy | El papel mide la fidelidad |
| Muy pocas operaciones tras filtrar | Minimo de operaciones por anyo fijado antes |
| El bot falla (ordenador apagado, red) | Se disenya en el paso 3; MT5 de Python solo va en Windows |
| El propietario no aguanta una racha mala | Mensajes de Telegram y freno; se habla antes del papel |
| La regla de una posicion elige mal | Regla fijada antes y comparada con la alternativa en la exploracion |

## 9. Decisiones pendientes (una por mensaje, en este orden)

1. Si el objetivo de la decision 1 (ganar al indexado) se aplica a las divisas.
2. Maximo de apalancamiento por par (que pares entran segun el valor de 1.000 unidades).
3. Umbral de la puerta del diagnostico.
4. Eventos del calendario y dias alrededor (tras verificar las fuentes).
5. Barreras: objetivo, stop, tiempo y freno mensual (rejilla pequenya).
6. Regla de una posicion.
7. Modelo y variables.
8. Duracion del papel.

## 10. Orden de trabajo (cada paso con su commit; puertas que pueden parar)

1. Fechas de inicio de los pares nuevos y fuentes del calendario y de los tipos (verificar).
2. Decisiones 1-3; diagnostico con los 7 principales (**puerta 1**).
3. Decisiones 4-8 y criterio completo **subido a git antes de bajar los pares nuevos**.
4. Bajar los pares nuevos; contraste con el BCE.
5. Exploracion (con las pruebas de fugas y de etiquetas al azar).
6. Reserva, una vez (**puerta 2**).
7. Papel (**puerta 3**). Despues, el bot.

## Anexo: inicio de los pares nuevos en Dukascopy (13/10/2026; solo tamanyo de ficheros, sin mirar precios)

Primer mes con datos, mirando enero y julio de cada anyo (aproximado a medio anyo):

| Desde | Pares |
|---|---|
| 2003 | USDZAR |
| 2004 | EURGBP, EURJPY, EURCHF, GBPJPY, AUDJPY, CHFJPY, GBPCHF, USDNOK, USDSEK |
| 2005 | EURCAD, CADJPY, USDSGD, EURNOK, EURSEK |
| 2006 | EURAUD, NZDJPY, AUDCAD, AUDCHF, GBPAUD, GBPCAD, EURNZD, GBPNZD |
| 2007 | AUDNZD (enero), USDMXN (julio) |

Los 25 tienen al menos ~7,5 anyos de exploracion (hasta 2014) y los 12 de reserva.
