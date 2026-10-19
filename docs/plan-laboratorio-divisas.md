# Plan del laboratorio de divisas en papel (19/10/2026)

Desarrolla la decision 14.1 (`docs/decisiones/14-replanteamiento.md`). Hecho con la entrevista del 19/10/2026 (11
decisiones del propietario, una por mensaje) y una revision de huecos con las skills de sobreajuste y de costes.
**Solo plan: no hay codigo ni datos.** La construccion empieza cuando el propietario lo diga (despues de la primera
senyal del bot de bolsa, 30/10, y de sus primeras operaciones, 02/11, si todo va bien).

## 1. Objetivo y usuario

Un banco de pruebas de ideas de divisas, en papel y hacia delante, con precios reales. Cada idea se escribe y se cuenta
**antes** de empezar y se juzga con un criterio ya fijado. Lo usa el propietario; la IA ayuda a proponer y explicar.

## 2. Reglas (decididas el 19/10/2026)

| # | Regla |
|---|---|
| 1 | **Banco de pruebas de ideas** (no una estrategia viva, no solo comentarios de la IA). |
| 2 | **La IA propone, el propietario aprueba.** Ninguna idea entra sin su si explicito; al entrar se fija en git con fecha. |
| 3 | **Hasta 2 ideas a la vez.** Una idea se cierra al llegar a su minimo de operaciones y su minimo de tiempo, fijados por escrito al entrar. |
| 4 | **Pasa** solo si: (a) gana dinero **despues de costes**; (b) confianza alta de que no es suerte, endurecida por el numero de ideas; (c) caida dentro del limite. Si falla una, se descarta. |
| 5 | **Apalancamiento ~4x con 250 €** (decision 13). Limites: caida maxima < 30 %, estres < 25 %, P(perder la mitad en 3 anyos) < 3 %. El apalancamiento solo multiplica; no rescata un resultado justo. |
| 6 | **Maxima frecuencia gratis: 1 minuto**, guardada cada dia desde el VPS (Yahoo solo da ~7 dias de minutos hacia atras: hay que acumularlos). |
| 7 | **IA diaria** durante 2 semanas; si consume mas del ~5 % del plan semanal, pasa a semanal. El 5 % es una propuesta y se ajusta a mano tras las 2 semanas. |
| 8 | **Se ve en el panel de bolsa** (seccion nueva) **y por Telegram**: avisos cuando una idea entra, pasa o se descarta, y un resumen semanal. |
| 9 | **Primero una idea, despues la infraestructura minima** para jugarla. Nada de construir todo antes (leccion de Ploutos). |
| 10 | **Plan ahora; construccion cuando el propietario lo diga.** |

## 3. Reglas anyadidas por la revision de huecos

- **Congelar la regla.** Una idea no se retoca una vez dentro: cambiar un parametro es una idea nueva y se cuenta.
- **El contador de pruebas incluye el pasado:** H2, el estudio 3 (27.315 operaciones), el fixing y toda idea del
  laboratorio cuentan para el liston contra la suerte.
- **Se juzga por la media por operacion con intervalo de confianza (bootstrap),** no por el Sharpe anualizado de 2
  meses (demasiado ruidoso). Minimo de operaciones **y** minimo de tiempo (propuesta: 3 meses) para cubrir regimenes.
- **Costes completos en el papel:** comision, spread simulado, **financiacion nocturna (swap) del apalancamiento** y
  huecos de fin de semana. Resultados a 1x, 2x y 3x los costes base. Margen de seguridad exigido: >= 2,5x (ganancia
  bruta / coste).
- **Salida del laboratorio:** si pasan 10 ideas sin ninguna aprobada, se cierra el laboratorio (propuesta; el
  propietario decide la cifra).
- **La IA guarda cada dia lo que leyo y lo que propuso** (reproducible y auditable). Su conocimiento del pasado puede
  influir en sus ideas: el papel hacia delante lo compensa.
- **Politica de huecos de datos:** si el VPS se para (como el reinicio del 19/10), los minutos perdidos no se
  recuperan; la idea afectada se anota y se decide si cuenta.

## 4. Bloqueos previos (no se arranca sin esto)

1. **Broker y vehiculo de las divisas (IBKR, CFD u otro) y sus costes reales, verificados.** Hoy solo hay la cifra de
   IBKR de `docs/estudios/viabilidad-otros-activos.md` (06/10/2026, minimo ~2 $ por orden): con 1.000 unidades son
   ~35 pb de coste fijo por viaje, sin spread. Con margen 2,5x haria falta ganar >= ~90 pb brutos por operacion, lo
   que descarta casi todo a escala de minuto. Puede cambiar la frecuencia del plan.
2. **Reglas del paso a dinero real** (decision 14.1: se fijan antes de arrancar; capital ~1.000 € sin apalancar o
   liston de riesgo M con los limites reales).
3. **Verificar que da Yahoo ahora** para divisas a 1 minuto (limites, huecos, ritmo de peticiones desde el VPS).
   **Hecho a medias (19/10/2026, yfinance, EUR/USD):** 1 minuto llega ~8 dias hacia atras (7d: 9.405 filas; 8d: 10.844);
   5 minutos, ~60 dias (16.968 filas desde el 28/07); 1 hora, ~730 dias (17.289 filas desde el 02/01/2024). **El
   volumen siempre es 0** (no hay volumen en divisas) y no hay spread: el coste se simula. **Sin comprobar:** huecos
   dentro de los minutos, otros pares, limites de peticiones desde el VPS.
   **Segunda prueba (19/10/2026, 5 dias de 1 minuto, los 7 pares):** GBP/USD, USD/JPY, USD/CHF y USD/CAD dan ~6.600
   filas (casi completos, solo el hueco del fin de semana). **AUD/USD y NZD/USD dan solo ~3.300: un precio cada 2
   minutos**, no cada uno. **EUR/USD repite el mismo precio en el 49 % de los minutos** (en los demas, 3-24 %): los
   minutos parecen rellenados o con poca actividad, y eso afecta a cualquier regla que mire el minuto. Es una muestra
   de 5 dias: hay que repetirla antes de fiarse. Sin comprobar: limites de peticiones desde el VPS.

## 5. Flujo

1. Se verifican los bloqueos (seccion 4).
2. La IA propone ideas con la regla ya escrita; el propietario aprueba o no (hasta 2 activas).
3. Cada idea se fija en git (regla, parejas, minimo de operaciones y de tiempo, criterio) **antes** de mirar nada.
4. Cada dia el VPS guarda los minutos; la regla se simula en papel con costes completos.
5. Al llegar a su minimo, se juzga con el criterio fijado: pasa o se descarta, y entra la siguiente.

## 6. Inputs y salidas

- **Entrada:** minutos de Yahoo (o la fuente que se verifique), noticias y comunicados de bancos centrales, calendario
  de eventos (estudio 3).
- **Salida:** seccion en el panel (ideas activas, operaciones simuladas, resultado, veredicto), avisos de Telegram y un
  resumen semanal.

## 7. Criterios de calidad

- Cada idea tiene regla y criterio escritos y subidos antes de medir.
- Los resultados se dan despues de costes, a 1x, 2x y 3x.
- El contador de pruebas esta al dia y se publica junto al veredicto.

## 8. Riesgos y ambiguedades pendientes

- Broker, costes y reglas de dinero real sin fijar (seccion 4).
- Cuanto gasta de verdad la IA diaria del plan del propietario: se mide en las 2 primeras semanas.
- Que aporta de verdad la IA frente a las ideas ya agotadas (tendencia, carry, fixings, H2): no esta probado.
- Capital de 250 € a 4x: un movimiento del ~25 % en contra borra la cuenta; el broker lo cerraria antes.

## 9. Siguiente accion

Cuando el propietario diga: verificar los bloqueos de la seccion 4 (en este orden), escribir la primera idea y
construir lo minimo para jugarla.

## 10. Estado de los bloqueos previos (19/10/2026)

**Bloqueo 2, reglas del paso a dinero real: RESUELTO** (decision del propietario, 19/10/2026).

1. Una idea que pasa su criterio en papel hace **3 meses mas de papel de confirmacion**, con la misma regla sin tocarla.
2. Si se sostiene, el propietario da su **si explicito** y se empieza con **la mitad del capital (125 €)**, mismo
   apalancamiento (~4x).
3. Tras **3 meses sin incidencias** a mitad de capital (propuesta, a confirmar), se sube a 250 €.
4. **Parada automatica en dinero real:** al perder el 30 % del capital asignado el bot deja de abrir operaciones y solo
   el propietario puede reanudarlo (mismo limite que la caida de la decision 13). Ademas, cada mes se compara el
   resultado real con el intervalo del papel; si cae fuera, se avisa y se pausa.

**Bloqueo 1, broker y costes: PARCIAL.** Las paginas oficiales de IBKR y de Trading 212 dieron error 403; solo hay resenyas
de terceros, sin verificar en la fuente:

- IBKR, divisas al contado: 0,2 pb del valor con minimo entre 2 $ y 2,50 $ por orden (dos fuentes discrepan). Con
  1.000 unidades (~1.160 $) son ~4 $ por viaje, **~35 pb: inviable** para ideas de corto plazo.
- Trading 212, CFD de divisas: sin comision declarada, el coste va en el spread (EUR/USD ~0,9-1,0 pips, ~1-2 pb por
  viaje) mas la financiacion nocturna (tasa de referencia mas un margen que no se ha encontrado). El limite de
  apalancamiento minorista de la UE en pares mayores es 30:1; ~4x queda por debajo.
- **Falta:** que el propietario confirme en la aplicacion (especificacion del producto EUR/USD en CFD) el spread, la
  financiacion nocturna y el apalancamiento de su cuenta, y que ofrece CFD de divisas. Hasta entonces, el simulador
  usara costes de tercero marcados como "sin verificar". El CFD es el vehiculo donde pierden el 70-90 % de los
  minoristas (CNMV): el apalancamiento sigue sin rescatar ningun resultado.

**Bloqueo 3, Yahoo: PARCIAL.** Hecho: ventanas, volumen y calidad de los minutos (seccion 4). **Falta** el limite de
peticiones desde el VPS, que no se prueba hasta despues del 02/11 (no tocar el VPS antes de las primeras operaciones).
Dado que AUD/USD y NZD/USD dan un precio cada 2 minutos y EUR/USD repite precio en el 49 % de los minutos, conviene
que las primeras ideas trabajen a 5 minutos o 1 hora, no a 1 minuto, hasta repetir la prueba con mas dias.

## 11. Bloqueo 1 resuelto: broker objetivo FOREX.com (19/10/2026)

**Decision del propietario:** el broker objetivo del laboratorio es **FOREX.com** (entidad europea de StoneX; oferta de
Irlanda/UE). Se decide asi tras descartar los otros dos:

- **Trading 212: descartado.** La clave API solo existe en cuentas Invest, no en CFD, y no hay cuenta demo para su
  entidad europea (respuesta del servicio de atencion al propietario, 19/10/2026): un bot no podria operar CFD de divisas.
- **IBKR al contado: descartado.** 0,2 pb con minimo de 2-2,50 $ por orden: ~35 pb por viaje con 1.000 unidades.
- **FOREX.com: elegido.** Tiene API REST para minoristas (cuentas Standard y Commission): se abre una cuenta real, se
  fondea y se pide a soporte que habiliten la API; la API demo solo se obtiene teniendo una cuenta real abierta.

**Costes que usa el simulador (de la web oficial de FOREX.com, leidos en una busqueda; verificar con cuenta):**
sin comision en CFD de divisas; spread EUR/USD desde 0,7 pips (pagina antigua, puede estar desfasada; otra pagina
anuncia 0,0 en cuenta RAW); financiacion nocturna de CFD en la UE: €STR +/- 3 % anual, base 360 dias (tabla de la web
australiana, por confirmar para la UE). **Todo se marca "sin verificar" hasta tener cuenta.**

**No hace falta cuenta de broker hasta que una idea pase** (todo el papel corre en el VPS). Cuando una idea pase y el
propietario quiera ir a real, se confirma con su cuenta: tamanyo minimo de operacion (si llega a 1.000 unidades),
proteccion de saldo negativo, porcentaje de cuentas minoristas que pierden, tabla de financiacion de la UE y la
activacion de la API.

**Estado final de los bloqueos:** 1 resuelto (esta seccion); 2 resuelto (seccion 10); 3 casi: falta solo el limite de
peticiones desde el VPS, que se prueba despues del 02/11.
