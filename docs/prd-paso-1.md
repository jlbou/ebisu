# Ebisu — PRD del paso 1: las decisiones de fondo (12/10/2026)

Resumen de la entrevista con el propietario del 11-12/10/2026. Cada decision tiene su documento en `docs/decisiones/`; si este PRD
y una decision no coinciden, manda la decision.

## 1. Objetivo

Un bot que **gane dinero, cuanto mas mejor**, con activos que no son cripto. Una estrategia solo pasa si, neta de
comisiones e impuestos, **gana mas que mantener un fondo indexado mundial, o lo mismo con claramente menos caida**
(decision 1). Si ninguna pasa, la respuesta es el indexado mantenido, sin bot (decision 7).

## 2. Usuario

El propietario, para si mismo. Particular residente en Espanya, sin ser experto, que quiere **no hacer nada** cuando el bot
funcione (decisiones 4 y 6). Ebisu convive con Ploutos, que sigue en marcha y no se toca.

## 3. Flujo paso a paso

1. **Decisiones de fondo** (este documento): HECHO.
2. **Verificaciones** antes del criterio: fondos indexados con traspaso (cuales, minimos, cuanto tarda un traspaso);
   brokers sin comision con fracciones de ETF europeos y API (p. ej. Trading 212: si opera en real, costes,
   regulacion); fuentes de datos historicos gratuitas.
3. **Criterio del estudio**, escrito y subido a git ANTES de medir: periodos (exploracion, reserva sin mirar mas larga
   que en Ploutos, prueba final), liston contra la suerte, impuestos operacion por operacion, la referencia (indexado
   con traspasos) y que es "claramente menos caida".
4. **Estudio con la historia** de las hipotesis 1-3 (`docs/hipotesis.md`); el apalancado, solo como informacion.
5. **Si alguna pasa:** elegir el vehiculo con el precio de automatizar delante; papel hacia adelante (y ahi, la
   hipotesis 4: la IA como filtro, contra el bot sin IA).
6. **Solo con el papel bien y la decision expresa del propietario:** construir el bot (reaprovechando Ploutos) y, despues,
   dinero real (250 €, la clave la pone el propietario en `.env`).

## 4. Entradas

- Precios historicos diarios de bolsa, bonos, oro y un monetario (indices o fondos); divisas para la hipotesis 2.
- Costes reales del vehiculo (comisiones, cambio de divisa, gasto anual del fondo) y las reglas fiscales espanyolas
  (19-28 % sobre la ganancia; regla de los dos meses en ETF; traspasos sin impuestos entre fondos).
- Noticias (solo para la hipotesis 4, en papel).

## 5. Salidas

- Del estudio: un veredicto por hipotesis con el criterio fijado antes (pasa / no pasa) y sus numeros.
- Del bot (si se llega): una rotacion mensual (o semanal) automatica; **cada mes un resumen por Telegram** escrito por
  la IA en palabras sencillas; el resumen fiscal anual en euros para la renta; avisos solo si algo falla.

## 6. Reglas principales

- **Mercado:** bolsa, bonos y oro siguiendo la tendencia (decision 2).
- **Capital maximo: 250 €** por ahora, sin aportaciones periodicas, dinero que no se necesita en 3 anyos (3 y 7).
- **Sin apalancamiento (1x), regla dura**: en el codigo y sin permiso de margen en el broker. El apalancamiento nunca
  rescata un resultado justo (decision 5).
- **La IA** explica siempre y puede reducir o aplazar una compra; nunca comprar, anyadir riesgo ni tocar el 1x (8).
- **Lista cerrada de hipotesis**; anyadir una es decision del propietario y cuenta para el liston (7).
- Nada de dinero real ni claves sin decision del propietario; secretos solo en `.env`; nunca "Claude" en la UI ni en Telegram.

## 7. Excepciones y casos limite

- **Ninguna hipotesis pasa:** indexado mantenido, sin bot; no se buscan ideas nuevas para salvar el proyecto.
- **Pasa solo por "menos caida" y gana pocos euros:** sigue sin apalancamiento.
- **Los ETF pierden mucho en impuestos frente a los fondos:** el propietario decide entre automatico y clic manual con el numero
  delante (decision 4).
- **Cambia la situacion del propietario** (capital, aportaciones): se revisan las decisiones 3 y 7.
- **El bot se para o el broker cambia algo:** aviso al propietario, que decide (poco a menudo, pero no nunca).
- **El veredicto de la fase 6 de Ploutos** (16/10-20/11) se tiene en cuenta antes de fijar el criterio de la hipotesis 4.

## 8. Criterios de calidad

- El criterio de cada prueba esta en git antes de medir; la reserva se mira una sola vez.
- Los numeros incluyen comisiones e impuestos reales; la referencia, el indexado con traspasos.
- Cada entrega al propietario se lee sola: que se ha hecho, que sale y que decision falta, con la recomendada marcada.

## 9. Riesgos y ambiguedades pendientes

- **Lo mas probable es que la tendencia pase, si pasa, solo por "menos caida"** (como L): pocos euros con 250 €.
- **Con ~12 decisiones al anyo, la prueba estadistica es debil:** hace falta mucha historia y una reserva larga.
- **Automatizar puede costar impuestos** (ETF) o no ser posible (fondos sin API). Sin verificar: los fondos y brokers.
- **La IA solo se puede juzgar hacia adelante:** meses de papel.
- Sin fijar todavia: que es "claramente menos caida", el fondo de referencia exacto y la duracion de cada periodo.

## 10. Siguiente accion recomendada

**Las verificaciones del punto 3.2** (fondos con traspaso, brokers con API, fuentes de datos), en un documento de
estudio con fuentes y fecha de lectura. Despues, el borrador del criterio del estudio para que el propietario lo apruebe antes de
medir nada.
