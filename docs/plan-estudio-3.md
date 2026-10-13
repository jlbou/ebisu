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
- ~4x (el minimo para 1.000 unidades con 250 €), exposicion total <= 4x sin divisas repetidas, calendario de eventos,
  compras y ventas, cierre los viernes, frenos mensual (15 %) y de la cuenta (175 €); liston de riesgo M.
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
| Tramos | Exploracion: desde el inicio de cada par hasta 2014; reserva: 2015-2026, una vez | Todos tienen >= 7,5 anyos de exploracion (anexo); se opera desde 2005 (T13) |
| Pares principales | Solo para disenyar y para el diagnostico | Ya vistos: nada de lo que digan es una prueba |
| Apalancamiento por par | **Decidido (13/10, opcion A): un par solo se opera si 1.000 unidades de su divisa base valen como mucho 4 veces lo que hay en la cuenta ESE dia** (cambio del dia). Con el cambio del BCE del 12/10/2026 entran 19 de 25 (fuera los de base GBP y CHFJPY) | Si la cuenta baja, entran menos pares; por debajo de ~150 € no se puede abrir ninguno (freno natural) |
| Calendario de eventos | Decisiones de bancos centrales (Fed, BCE, BoE, BoJ, SNB, RBA, BoC, RBNZ, Norges, Riksbank), empleo de EE. UU., referendums y elecciones, 2003-2026 | **Sin comprobar que existan calendarios historicos completos y gratuitos** |
| Tipos de interes por divisa | Para los intereses de cada noche del CFD | Fuentes oficiales por divisa (sin comprobar); el recargo del broker, de su web |

## 4. Diagnostico (puerta 1, antes de disenyar reglas o modelo)

Con los 7 principales (ya vistos), compras en el minimo y ventas en el maximo de ayer, con las tres barreras, ~4x y
las reglas fijas (cierre del viernes, horas y fechas sin abrir, pares con cambio fijado, veto de eventos aparte): clasificar las perdidas
grandes por escenario y de cada peor perdida, que pasaba ese dia. Barreras provisionales solo para el diagnostico: objetivo
en la mitad del rango de ayer, stop de un rango medio (20 dias), maximo 5 dias.

Escenarios marcados **antes** de comprar (umbrales de manual, fijados el 13/10):
1. Evento programado ese dia o el anterior.
2. Tendencia a la baja: precio por debajo de su media de 200 dias y la media bajando.
3. Volatilidad disparada: rango de ayer > 2 veces el rango medio de 20 dias.
4. Huida del riesgo: VIX en el 10 % mas alto de su ultimo anyo.
5. Rotura del minimo de las ultimas 20 sesiones.

**Pasa la puerta (opcion A del propietario, 13/10)** si se cumplen las tres:
- las operaciones no marcadas ganan de media tras costes (resultado medio por operacion > 0);
- quedan al menos el 40 % de las operaciones;
- las marcadas contienen al menos la mitad de las peores perdidas (el 5 % peor de las operaciones).

Si no pasa, se para aqui y se le explica al propietario. Si pasa, solo dice que vale la pena seguir (datos ya vistos).

## 5. Las capas, una a una

| Capa | Que hace | Decisiones pendientes | Como no enganyarnos |
|---|---|---|---|
| 1. Senyal | Comprar si el ask baja 1 pip por debajo del minimo de ayer; vender si el bid sube 1 pip por encima del maximo (T17, P2) | - | Cruzar el nivel, no solo tocarlo |
| Posiciones | **Decidido (13/10, opciones A y B):** exposicion total de todas las posiciones abiertas <= 4 veces la cuenta del dia y **ninguna divisa repetida** entre posiciones abiertas (con 250 €, una sola); si saltan varios pares, se coge **el primero que toca su minimo** (por horas) | - | Sin parametros ni datos del futuro |
| 2. Reglas (veto) | **Decidido (13/10, opcion A):** si hay evento hoy o manyana, no se abre; si hay una posicion abierta, se cierra el dia antes. Eventos: decisiones de los bancos centrales de las dos divisas del par, empleo de EE. UU. (todos los pares) y **todas** las elecciones generales y referendums nacionales de los paises de esas divisas (ver anexo) | - | Listas completas de fuentes publicas, sin elegir a mano cuales |
| 3. Modelo | **Decidido (13/10, opcion A): regresion logistica** (dependencia nueva: scikit-learn). Entra si la probabilidad supera el porcentaje medio de aciertos del entrenamiento (sin umbral que elegir). Se reentrena cada anyo con todo el pasado | - | Validacion anidada y purgada (purga 10 dias, el limite de tiempo maximo), CPCV, PBO, coeficientes estables, prueba con etiquetas al azar; ninguna variable > 40 % del peso |
| 4. Proteccion | **Decidido (13/10, opcion A):** objetivo en la mitad del rango de ayer; stop a 0,75 / 1 / 1,5 rangos medios (20 dias) bajo la entrada; limite de 3 / 5 / 10 dias; freno mensual fijo: si el mes pierde > 15 %, no se opera mas ese mes y se avisa | - | Rejilla de 9 combinaciones (cuentan como pruebas); pasa si >= 6 de 9 ganan dinero, sin precipicios ni el optimo en el borde |
| 5. IA | Lee noticias; solo puede frenar | Que lee y cuando: se decide antes del papel (no entra en el estudio) | No se puede probar con la historia: solo en papel, en sombra |

## 6. Costes y fiscalidad reales

- Diferencial real (compra y venta de Dukascopy) **mas el recargo del broker de CFD** (sin comprobar; el de su web).
- Intereses de cada noche: diferencia de tipos + recargo del broker, x ~4.
- Ejecucion: stop en un salto = primer precio disponible despues del salto (peor que el stop).
- Comparar siempre con y sin costes (cost-model).
- Fiscalidad de los CFD en Espanya: **sin comprobar** (probablemente ganancia patrimonial al 19 %).

## 7. Cuando pasa (todas, fijadas antes de medir la reserva)

1. Gana dinero neto (TAE > 0 tras costes, intereses e impuestos).
2. **Objetivo de la decision 1, igual que siempre** (decidido el 13/10, opcion A): gana al indexado mundial mantenido,
   o lo iguala (a menos de 1 punto) con una caida de como mucho 2/3 de la suya. Si no, el riesgo de ~4x no compensa.
3. No es suerte: Sharpe deflactado >= 0,95 contando **todas** las pruebas (tambien las informales del punto 2.4), y
   PBO < 0,5.
4. Liston de riesgo M (decision 13).
5. Robustez y estabilidad: > 60 % de la rejilla con Sharpe > 0; la mejora sale en la mayoria de pares, no solo en el
   total; perdida de rendimiento fuera de muestra < 30 % (y sospecha si es < 5 %: fuga).

Despues: **papel de 3 meses** (decidido el 13/10, opcion A) en la **cuenta demo del broker de CFD** (sus precios,
diferenciales e intereses), con las condiciones de la decision 11; y solo entonces dinero real.

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

1. ~~Si el objetivo de la decision 1 se aplica a las divisas~~: si, igual (opcion A, 13/10).
2. ~~Maximo de apalancamiento por par~~: 4x sobre la cuenta del dia (opcion A, 13/10).
3. ~~Umbral de la puerta del diagnostico~~: opcion A (13/10).
4. ~~Eventos del calendario~~: opcion A (13/10).
5. ~~Barreras~~: rejilla de 9 y freno del 15 % (opcion A, 13/10).
6. ~~Regla de una posicion~~: la primera en el tiempo (opcion A, 13/10).
7. ~~Modelo y variables~~: regresion logistica con combinaciones a mano (opcion A, 13/10).
8. ~~Duracion del papel~~: 3 meses en la demo del broker (opcion A, 13/10).

## 10. Orden de trabajo (cada paso con su commit; puertas que pueden parar)

1. Verificaciones: calendarios (solo reuniones programadas) y elecciones, tipos de interes, un broker de CFD concreto
   (pares, diferencial, recargos, conversion a euros, demo, API) y fiscalidad de los CFD.
2. Diagnostico con los 7 principales (**puerta 1**).
3. Criterio completo **subido a git antes de bajar los pares nuevos**.
4. Bajar los pares nuevos (dias: Dukascopy es lento); contraste con el BCE.
5. Exploracion (con las pruebas de fugas y de etiquetas al azar).
6. Reserva, una vez (**puerta 2**).
7. Papel de 3 meses en la demo (**puerta 3**). Despues, el bot.

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

## Anexo: calendario de eventos (decision 4, opcion A; 13/10/2026)

Regla para no elegir a mano: se incluyen **todos** los de cada lista, salgan como salgan.

| Divisa | Banco central | Elecciones y referendums nacionales |
|---|---|---|
| USD | Fed (FOMC) + empleo de EE. UU. (BLS) para todos los pares | Presidenciales y legislativas (midterms) |
| EUR | BCE | Generales o presidenciales de Alemania, Francia, Italia y Espanya (las 4 mayores economias del euro) y sus referendums nacionales; referendum griego de 2015 |
| GBP | Banco de Inglaterra | Generales; referendums del Reino Unido (2011, 2016) y el de independencia de Escocia (2014) |
| JPY | Banco de Japon | Camara de Representantes y Camara de Consejeros |
| CHF | Banco Nacional Suizo | Federales y **todas** las votaciones populares federales |
| AUD, CAD, NZD, NOK, SEK | RBA, BoC, RBNZ, Norges Bank, Riksbank | Generales y referendums nacionales |
| MXN, ZAR, SGD | Banxico, SARB, MAS | Generales (y presidenciales) |

Fuentes: archivos oficiales de cada banco central y del BLS; elecciones, listas publicas por pais. Si alguna lista no se
puede completar desde 2003, se dice y ese par se marca.

## Anexo: variables del modelo (decision 7, opcion A; 13/10/2026)

Todas con datos de antes de entrar (retrasadas), normalizadas con ventanas moviles de cada par:

1. Tendencia: distancia a la media de 200 dias (en rangos medios) y pendiente de la media.
2. Volatilidad: rango de ayer / rango medio de 20 dias; percentil de la volatilidad de 20 dias en el ultimo anyo.
3. Miedo: percentil del VIX en el ultimo anyo.
4. Minimos: distancia a los minimos de 20 y 60 dias (en rangos medios).
5. Rendimiento de 1, 5 y 20 dias (en rangos medios).
6. Eventos: dias hasta el proximo y desde el ultimo.
7. Movimiento conjunto: cuantos pares mas tocan su minimo ese dia (hasta la hora de entrada).
8. Hora, dia de la semana y diferencial relativo en la entrada.
9. Combinaciones dadas a mano (la logistica no las ve sola): tendencia a la baja x volatilidad alta; tendencia a la
   baja x miedo alto; rotura del minimo de 20 dias x volatilidad alta.

## 11. Revision del plan: agujeros encontrados (13/10/2026)

Revision pedida por el propietario, con las skills `ml4t-model-validation`, `ml4t-cost-model`, `ml4t-data-leakage` y
`ml4t-backtest-overfitting`. Los tecnicos se cierran asi (el propietario puede discutirlos); los de decision se le
preguntan uno a uno.

### Tecnicos (cerrados con el criterio prudente)

| # | Agujero | Como se cierra |
|---|---|---|
| T1 | El calendario incluiria reuniones de urgencia (p. ej. la Fed en marzo de 2020), que nadie sabia de antemano: seria mirar el futuro | Solo reuniones **programadas** (publicadas antes); las de urgencia cuentan como sorpresa |
| T2 | Elecciones anticipadas; eventos en fin de semana | Cuentan desde el dia en que se anuncian, no antes; si el evento cae en sabado o domingo, "el dia antes" es la ultima sesion antes del evento |
| T3 | Cerca de las 17:00 de Nueva York (cambio de dia) y del 24/12 al 2/1 los diferenciales se disparan | No se abre entre las 16:00 y las 18:00 de Nueva York ni del 24/12 al 2/1 |
| T4 | No estaba claro que va a la reserva | En la exploracion, cada candidata (5 capas y solo reglas = capas 1, 2 y 4) elige su mejor combinacion de las 9, y solo pasa a la reserva si >= 6 de 9 ganan dinero; a la reserva van las dos (liston de confianza corregido por ser dos, como en el estudio 2) |
| T5 | Numero de pruebas sin cifrar | N = 30: 5 (estudio 1) + 2 (estudio 2) + 1 (H2 reserva) + 4 (miradas informales) + 18 (9 x 2 candidatas); la varianza, de las 18 de este estudio |
| T6 | Con que datos aprende el modelo | Todos los pares (principales y nuevos), solo operaciones cerradas **10 dias antes** de cada reentreno (purga comun a todos los pares, porque el mismo dia afecta a todos) |
| T7 | Que es "salir bien" | Resultado neto > 0 tras diferencial, intereses y recargos |
| T8 | El resultado de cada operacion esta en otra divisa y el broker puede cobrar por pasarlo a euros | A verificar con el broker; se suma al coste |
| T9 | El broker elegido quiza no tiene los 25 pares | Se fija la lista con los que tenga **antes** de bajar los datos |
| T10 | Intereses: el miercoles se cobran 3 noches (fin de semana) | Se simula asi |
| T11 | Fiscalidad de los CFD | A verificar antes de medir |
| T12 | La referencia ya se conoce: el indexado hizo 10,54 % al anyo con una caida del 33,6 % en 2015-2026 | Condicion 2 en cifras: TAE >= 10,54 %, o >= 9,54 % con caida <= 22,4 % |
| T13 | Los pares nuevos empiezan en 2004-2007 y el modelo necesita pasado | El primer modelo aprende con los principales desde 2003; se opera desde 2005 |
| T14 | El freno mensual sobre que | Sobre el valor de la cuenta el primer dia del mes |
| T15 | "Minimo de operaciones" sin cifrar | Al menos 30 operaciones al anyo de media en la exploracion |
| T16 | El contraste de datos solo cubria los cruces del euro | Todos los pares se pueden contrastar con el BCE (cruces de sus cambios de referencia) |
| T17 | La senyal "cruzar" sin cifrar | El ask tiene que bajar al menos 1 pip por debajo del minimo de ayer |

### De decision del propietario (pendientes, en este orden)

| # | Agujero | Por que importa |
|---|---|---|
| P1 | **Como se define la prueba de estres** — **decidido (13/10, opcion A):** se hace correr la estrategia real (reglas, veto, modelo, stops con salto) por una lista fija de crisis: 2008 (sept.-oct.), 6/05/2010, agosto de 2011, 15/01/2015, 24/06/2016, febrero de 2018, marzo de 2020, agosto de 2024 y abril de 2025; pasa si en ninguna pierde > 25 %. Ademas, **no se operan pares con un tipo de cambio fijado o con suelo oficial** mientras dure (EUR/CHF del 6/09/2011 al 15/01/2015). El peor caso imaginario (posicion en el peor par en el peor momento) se informa, no decide | Si se supone "una posicion abierta en el peor par en el peor momento", EUR/CHF el 15/01/2015 (-30 % en minutos) a 4x deja la cuenta a cero y **ninguna estrategia pasaria nunca**. Hay que definirla de forma justa |
| P2 | Solo compras, o tambien la version espejo — **decidido (13/10, opcion B): las dos, como una sola estrategia.** Compra si el ask baja 1 pip por debajo del minimo de ayer; vende si el bid sube 1 pip por encima del maximo de ayer; objetivo en la mitad del rango de ayer y stop al otro lado. Los escenarios y las variables se miran en el sentido de cada operacion (tendencia en contra, rotura del maximo de 20 dias para las ventas). El diagnostico informa compras y ventas por separado. Intereses de cada noche con el signo de cada lado | Las divisas son simetricas; con solo compras la estrategia es la mitad |
| P3 | Fin de semana — **decidido (13/10, opcion B): todo se cierra el viernes antes de las 16:00 de Nueva York**, y el viernes a partir de esa hora no se abre nada | El limite de 3-10 dias cruza fines de semana: riesgo de salto el lunes |
| P4 | Si la cuenta baja — **decidido (13/10, opcion B): freno de la cuenta en 175 € (-30 %)**: el bot cierra todo, se para y avisa; solo vuelve si el propietario lo decide tras revisar que paso. Nunca se anyade dinero automaticamente | El bot se para y avisa; hay que decidir si es el final o si se rehace |

## 12. Segunda revision (13/10/2026)

Pedida por el propietario. Busca contradicciones entre las decisiones nuevas (ventas, viernes, freno de la cuenta) y
lo ya escrito. Corregidas en el texto: secciones 1, 3, 4, 5 y 10. Ademas:

### Tecnicos (cerrados)

| # | Agujero | Como se cierra |
|---|---|---|
| F1 | "Mejor combinacion" de la rejilla sin metrica | La de mayor Sharpe de la cuenta diaria neta en la exploracion |
| F2 | El freno mensual no decia que pasa con lo abierto | Al saltar, se cierra todo y no se abre nada hasta el mes siguiente |
| F3 | Los frenos, sobre que valor | Sobre el valor de la cuenta con lo abierto a precio de mercado (hora a hora) |
| F4 | El 4x se mira al abrir; si la cuenta cae con una posicion abierta, el apalancamiento real sube | Se acepta: con el freno en 175 €, como mucho ~5,7x antes de cerrar todo. Se informa |
| F5 | Dos senyales del mismo par (toca minimo y maximo el mismo dia) | Una posicion por par; mientras esta abierta, el par no da senyales |
| F6 | Compras y ventas en el modelo | Un solo modelo; el sentido es una variable mas y todas las demas se miran en el sentido de la operacion |
| F7 | Una rejilla, un modelo | Cada una de las 9 combinaciones tiene sus etiquetas y su modelo |
| F8 | La logistica con ~20 variables se puede sobreajustar | Variables estandarizadas con datos de entrenamiento y regularizacion por defecto (L2, C = 1), sin buscarla |
| F9 | El diferencial del broker de CFD suele ser mayor que el de Dukascopy | Se usa el mayor de los dos: el de los datos o el tipico publicado por el broker para ese par |
| F10 | Los stops en movimientos rapidos dentro de la hora | El stop se ejecuta 1 diferencial peor; si la hora abre ya mas alla, al precio de apertura |
| F11 | Los intereses historicos del broker no existen | Diferencia de tipos oficiales de cada dia + el recargo actual del broker aplicado a toda la historia |
| F12 | El resultado de cada operacion esta en otra divisa | Se pasa a euros con el cambio del momento, mas el recargo de conversion del broker si lo cobra (T8) |
| F13 | Volumen de datos | 25 pares x 2 lados x ~260 meses: ~13.000 ficheros; con la experiencia del estudio 1, varios dias |

### De decision del propietario

| # | Agujero | Por que importa |
|---|---|---|
| P5 | **El freno de la cuenta (175 €) esconde el riesgo en la condicion 1 del liston M** — **decidido (13/10, opcion A): el riesgo se mide SIN el freno de la cuenta** (con el freno mensual, que es parte de la estrategia); el freno de 175 € es solo red de seguridad. Se informa ademas la probabilidad de que salte en 3 anyos | Con el freno, la cuenta casi nunca puede llegar a 125 € (solo con un salto), asi que "perder la mitad" saldria casi siempre bien aunque la estrategia fuera muy arriesgada. Hay que decidir si el riesgo se mide con o sin la red |

## 13. Verificaciones (paso 1; 13/10/2026, en curso)

### 13.1 Broker de CFD (fuentes de los brokers y terceros, leidas el 13/10/2026)

| | Dukascopy Europe (Letonia, Banco de Letonia) | Capital.com (Chipre, CySEC) |
|---|---|---|
| Datos del estudio | **Son sus propios precios** (los de Dukascopy): maxima fidelidad | Precios propios, distintos |
| Comision | 35 $ por millon y lado con < 5.000 $ depositados: ~0,035 $ por operacion de 1.000 unidades | Ninguna |
| Diferencial | El de los datos (mercado) | Variable, sin tabla publicada; suele ser mayor |
| Intereses de cada noche | Tipos de los bancos centrales + su recargo, segun la actividad del cliente (sin cifra publica) | 0,00411 % diario (~1,5 % al anyo) +/- tom-next |
| Pasar el resultado a euros | 0,1 % | 0,7 % (incluido en el cambio) |
| Deposito minimo | 100 $ | 20 € |
| API y demo | JForex (Java) y FIX; MT4 (1:30) y MT5 "en desarrollo"; demo si | REST (facil desde Python) con demo propia |
| Pares | 300+ cruces desde 06/2025; algunos de los nuestros salieron primero solo en demo; AUD/NZD sin confirmar | 120+ pares; lista exacta sin confirmar |
| Minimo por operacion | 1.000 unidades | "500" sin unidad clara; 0,01 lotes segun terceros |
| Saldo negativo | Protegido (no se pierde mas que lo depositado) | Protegido (ESMA) |
| Autorizado en Espanya (pasaporte UE) | **Sin confirmar** (buscar en el registro de la CNMV) | **Sin confirmar** |

**No se puede cerrar sin una cuenta demo:** la lista exacta de pares, los minimos por par, los diferenciales tipicos y
los intereses reales solo los da la plataforma (en Capital.com, `GET /markets` de la API con una sesion de demo). Abrir
una demo es decision del propietario (sin dinero; las claves irian al `.env`).

Fuentes: [Capital.com, API](https://open-api.capital.com/), [Capital.com, comisiones UE](https://capital.com/en-eu/ways-to-trade/fees-and-charges),
[Capital.com, intereses](https://capital.com/overnight-fees), [Dukascopy Europe, tarifas](https://www.dukascopy.com/europe/english/about/fee-schedule),
[Dukascopy, intereses](https://www.dukascopy.com/europe/english/forex/forex_trading_accounts/overnight/?ibref=8514),
[Dukascopy, cruces nuevos](https://www.financemagnates.com/forex/dukascopy-adds-303-cross-instruments-to-let-traders-move-beyond-usd-pairs/).

### 13.2 Fiscalidad de los CFD en Espanya

- Ganancias y perdidas patrimoniales en la **base del ahorro** (DGT, consultas vinculantes V0076-09, V1342/2014 y
  V0597/2018): 19 % hasta 6.000 €, despues 21 %, etc. (comprobar la tabla vigente en la AEAT).
- Se imputan por anyo; perdidas compensables los 4 anyos siguientes; las comisiones cuentan. La regla de los dos meses
  no parece aplicar a los CFD (solo foros: sin confirmar). Los intereses de financiacion: trato distinto segun el lado
  (sin confirmar). **El simulador aplica: neto anual al 19 %, perdidas 4 anyos, sin regla de dos meses, intereses como
  coste** (lo prudente si no fueran deducibles es el peor caso: se informara con y sin).

Fuentes: [CMC Markets, fiscalidad](https://www.cmcmarkets.com/es-es/documentos-legales/trading-cfd),
[Rankia, fiscalidad CFD](https://www.rankia.com/blog/contratos-por-diferencias/1532494-fiscalidad-cfds),
[consulta DGT](https://www.fiscal-impuestos.com/sites/fiscal-impuestos.com/files/NFC068169.pdf).

### 13.3 Tipos de interes por divisa

- **BIS, tipos oficiales de los bancos centrales, diarios** (`WS_CBPOL`): estan AU, CA, CH, GB, JP, MX, NO, NZ, SE, US,
  zona euro (XM) y ZA. **Falta SGD** (la autoridad de Singapur no tiene tipo oficial: habria que usar el SORA de la
  MAS, sin comprobar desde cuando).
- Las series de la OCDE en FRED estan desactualizadas en varios paises: no sirven.

Fuente: [BIS en DBnomics](https://db.nomics.world/BIS/WS_CBPOL).

### 13.4 Broker elegido: Dukascopy Europe (13/10/2026, opcion A del propietario), con 5 comprobaciones

Motivo: los datos del estudio son sus precios (fidelidad), costes menores (comision minima, 0,1 % al pasar a euros).
La API (JForex, Java) es el inconveniente: la parte que envia ordenes iria en Java; el estudio, el modelo y Telegram,
en Python. FIX: parece pedir un deposito alto (sin confirmar). MT5: "en desarrollo". Nada de puentes no oficiales.

| # | Comprobacion | Resultado |
|---|---|---|
| 1 | Autorizado en Espanya | **Confirmado (CNMV, consultado el 13/10/2026):** DUKASCOPY EUROPE IBS AS, empresa de servicios de inversion del EEE en libre prestacion, registro n.º 2989 desde el 29/08/2011; autorizada, entre otros, para recibir y ejecutar ordenes de clientes en derivados sobre divisas y **contratos financieros por diferencias** ([ficha](https://www.cnmv.es/portal/Consultas/esi/esisextranjeraslp?tipo=CLP&numero=2989&vista=17)) |
| 2 | Duracion de la demo | **14 dias**, sin forma documentada de alargarla. El papel de 3 meses no cabe en una demo: habra que decidir como hacerlo antes del papel |
| 3 | Que pares hay de verdad | **Comprobado por el propietario en la demo de Dukascopy Europe (14/10/2026):** 298 pares de divisas; estan los 8 dudosos (AUD/NZD, USD/SGD, USD/ZAR, USD/MXN, EUR/NOK, EUR/SEK, USD/NOK, USD/SEK), asi que estan los 25. Importe por defecto: 1.000 unidades. Ordenes de mercado, limite, MIT y stop, con stop y objetivo en la orden. Limite: estar en la demo no garantiza del todo poder operarlo en real (se comprueba al final del papel) |
| 4 | Cuenta en euros | **Si**: EUR esta entre las divisas de cuenta. Deposito minimo 100 $ o equivalente |
| 5 | Recargo de los intereses | **No es publico**: depende de la actividad del cliente (mas actividad, mejores condiciones). En el estudio, el caso prudente |

Fuentes: [Dukascopy Europe, cuentas](https://www.dukascopy.com/europe/english/forex/forex_trading_accounts/),
[demo](https://www.dukascopy.com/swiss/english/forex/demo-fx-account/),
[registro belga](https://www.fsma.be/en/party/dukascopy-europe-ibs),
[Banco de Letonia](https://uzraudziba.bank.lv/en//market/investment-service-providers/investment-firms/dukascopy-europe-ibs-as).

### 13.5 Calendario de eventos: fuentes por banco central (13/10/2026)

| Banco | Fuente historica | Estado |
|---|---|---|
| Fed (USD) | Paginas historicas por anyo del FOMC: "Meeting" (programada) frente a "Conference Call" (urgencia) | Completa desde 2003 |
| BCE (EUR) | Comunicados de cada decision (archivo de prensa por anyo); mensual hasta 2014, cada 6 semanas desde 2015 | Por montar, existe |
| Banco de Inglaterra (GBP) | Actas del MPC por anyo desde 1997 y las fechas anuales publicadas cada septiembre | Completa |
| Banco de Japon (JPY) | Actas por anyo y calendarios anuales | Completa |
| SNB (CHF) | Evaluaciones trimestrales (marzo, junio, septiembre, diciembre) | Por montar, existe |
| RBA (AUD) | Comunicados de cada reunion (11 al anyo hasta 2023, 8 desde 2024) | Por montar, existe |
| BoC (CAD) | Calendarios anuales de anuncios (fechas fijas desde finales de 2000) | Por montar; 2003-2005 sin confirmar |
| RBNZ (NZD) | Cronologia oficial de anuncios desde 11/1999 | Completa |
| Norges Bank (NOK) | Archivo de decisiones desde 1986 | Completa |
| Riksbank (SEK) | Decisiones en su web desde 2017 | **Antes de 2017, sin confirmar** |
| Banxico (MXN) | Calendario desde 2003 (antes no habia) | **Sin confirmar el archivo completo** |
| SARB (ZAR) | Comunicados de cada reunion; algunos anyos sueltos | **Sin confirmar el archivo completo** |
| MAS (SGD) | Tabla oficial de decisiones desde 2001 (semestral hasta 2023, trimestral desde 2024) | Completa |
| Empleo de EE. UU. | Archivo de la BLS (cada informe con su fecha) | Completa |
| Elecciones y referendums | Listas publicas por pais (Wikipedia) | Por montar |

Regla ya fijada (anexo de la decision 4): si un calendario no se puede completar desde 2003, se dice y el par se marca
(SEK, MXN y ZAR, los dudosos).

Fuentes: [Fed](https://www.federalreserve.gov/monetarypolicy/fomc_historical_year.htm),
[BoE](https://www.bankofengland.co.uk/sitemap/minutes), [RBNZ](https://www.rbnz.govt.nz/monetary-policy/monetary-policy-decisions),
[Norges Bank](https://www.norges-bank.no/en/topics/monetary-policy/policy-rate/Key-policy-rate-Monetary-policy-meetings-and-changes-in-the-policy-rate/),
[Riksbank](https://www.riksbank.se/en-gb/monetary-policy/monetary-policy-report/),
[MAS](https://www.mas.gov.sg/monetary-policy/past-monetary-policy-decisions),
[SNB](https://www.snb.ch/en/the-snb/mandates-goals/monetary-policy/decisions),
[RBA](https://www.rba.gov.au/media-releases/2024/mr-24-09.html),
[BoC](https://bankofcanada.ca/?p=8075), [SARB](https://www.resbank.co.za/en/home/what-we-do/monetary-policy/monetary-policy-committee),
[Banxico (calendario 2016)](https://www.banorte.com/dam/jcr:fbca23fa-d57f-4bf7-b6d3-19be15b67010/0042_20151209_CalendarioBanxico2016.pdf),
[BLS](https://www.bls.gov/bls/news-release/empsit.htm), [VIX](https://fred.stlouisfed.org/graph/?g=1DU0C).
