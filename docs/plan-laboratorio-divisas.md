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
