# Estudio 3 (divisas): las dos opciones desarrolladas, para decidir (13/10/2026)

Viene de `docs/estudios/recerca-divisas.md`. **Nada medido.** El propietario pide desarrollar las dos opciones y
compararlas. Exploracion y prueba con **pares que no se han tratado** (el propietario acepta que no sean independientes
de los principales: se pareceran mas a lo que se operaria). Los 7 pares principales, ya vistos, solo sirven para
disenyar.

## 0. Lo comun a las dos

- **Senyal base (la de siempre):** comprar cuando el ask toca el minimo de ayer, a ese precio, sin apalancamiento.
- **Salida con tres barreras** (para que ninguna operacion quede atrapada anyos, el problema del 1 %): objetivo (la
  mitad del rango de ayer, como propuso el propietario), limite de tiempo y una perdida maxima de emergencia. Los
  valores se fijan antes de medir (decision aparte).
- **Datos:** velas de 1 hora de Dukascopy (compra y venta reales: el diferencial ya cuenta). Pares nuevos: exploracion
  2003-2014 y reserva 2015-2026, como siempre. Costes reales e impuestos al 19 %.
- **Primer paso, igual para las dos (diagnostico, con los 7 principales ya vistos):** clasificar las compras perdedoras
  por escenario. Si las perdidas **no** se concentran en escenarios reconocibles, ninguna de las dos opciones puede
  funcionar, y se sabe antes de gastar mas.
- **Variables del momento de la senyal** (las mismas para las dos; nunca con datos posteriores):

| Escenario | Variable | Fuente |
|---|---|---|
| 1. Noticia programada | Hay decision de la Fed o del BCE, o empleo de EE. UU., hoy o manyana | Calendarios oficiales historicos (sin comprobar que esten completos desde 2003) |
| 2. Tendencia en contra | Precio frente a su media de 100 y 200 dias; pendiente | Precios |
| 3. Volatilidad disparada | Rango de ayer / rango medio de 20 dias | Precios |
| 4. Huida del riesgo | Cuantos pares caen a la vez; VIX | Precios; VIX en FRED (sin comprobar) |
| 5. Rotura de un minimo mayor | El minimo de hoy rompe el de 20 o 60 dias | Precios |
| 6. Cambio de regimen | No se ve con precios: lo cubren el limite de tiempo y la perdida maxima | - |

## 1. Opcion A: reglas por escenario

**Como funciona:** para cada escenario, una regla sencilla con umbral de manual (no buscado en los datos): por
ejemplo, "no se compra el dia de la Fed", "no se compra si el precio esta por debajo de su media de 200 dias y
bajando", "no se compra si el rango de ayer es mas del doble de lo normal". Se escriben antes de mirar los pares
nuevos; la exploracion solo dice cuales se quedan (se cuentan todas las combinaciones probadas).

| Pros | Contras |
|---|---|
| Se entiende: el bot puede explicar "hoy no compro porque hay Fed" (encaja con la IA analista de la decision 8) | Los umbrales son de manual: pueden no ser los buenos |
| Pocos parametros: poco riesgo de ajustarse al pasado | Puede quitar demasiadas operaciones y quedarse sin ganancia |
| Cada regla tiene una razon economica (la literatura) | Solo trata los escenarios que se nos han ocurrido |
| Sin dependencias nuevas; se construye rapido | Las reglas se solapan: una sola quiza hace todo el trabajo |

## 2. Opcion B: que el bot aprenda (meta-etiquetado)

**Como funciona:** cada compra pasada se etiqueta como buena o mala (con las tres barreras). Un modelo sencillo
(regresion logistica o arboles) aprende, con las variables de la tabla y algunas mas (dia de la semana, hora,
diferencial, rendimientos recientes), la probabilidad de que una compra salga bien. El bot solo compra por encima de
un umbral, y puede poner mas o menos dinero segun la probabilidad.

Para no enganyarnos: entrenar y validar por bloques de tiempo con separacion entre ellos (purga y embargo de Lopez de
Prado), el modelo y el umbral fijados al final de la exploracion, y la reserva mirada una vez.

| Pros | Contras |
|---|---|
| Encuentra combinaciones que a nadie se le ocurririan | **Riesgo alto de ajustarse al pasado** y de fugas de datos si se hace mal |
| Da una probabilidad: permite apostar menos cuando duda | **Las perdidas catastroficas son pocas** (decenas en 12 anyos): el modelo apenas puede aprender de ellas |
| Es "que el bot sepa leer los casos" | Caja negra: cuesta explicar por que no compra |
| Se puede reentrenar con datos nuevos | Dependencia nueva (scikit-learn) y mas trabajo; cada reentrenamiento es otra variante |

## 3. Lo estadistico (aplica a las dos)

- **Colas gordas:** el resultado medio por operacion lo deciden pocos dias muy malos. Se informa media **y** mediana, y
  la peor operacion; un filtro que "mejora la media" quitando 5 dias raros de la exploracion es sospechoso.
- **Potencia:** con una ventaja de ~0,04 % por operacion y una desviacion de ~0,4 %, hacen falta ~300-550
  operaciones para distinguirla de cero al 90-99 %. Hay de sobra (~1.500 por par y tramo), **pero** las operaciones de
  varios pares el mismo dia estan correlacionadas: el numero efectivo es menor. Se usa el Sharpe probabilistico sobre
  la cartera diaria (como en el estudio 2), no las operaciones sueltas.
- **Por par:** que la mejora salga en la mayoria de los pares nuevos, no solo en el total (una mejora que solo esta en
  un par es casualidad o un par raro).
- **Muchas pruebas:** cada regla o modelo probado en la exploracion se cuenta (Sharpe deflactado), como en el estudio 1.

## 4. Opcion C: las dos en paralelo

Comparten el 80 % del trabajo (datos, etiquetas, variables, simulador). A la reserva irian la mejor de A y la mejor de
B, con el liston corregido por ser dos.
