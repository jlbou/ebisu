# Decision 12: que pasa si la reserva del estudio 2 no da ganadora (13/10/2026; fijado ANTES de medir)

Opcion A + C del propietario, decidida **antes** de medir la reserva del estudio 2, para que el resultado no influya.
Cambia el "se cierra Ebisu, sin mas intentos" de `docs/decisiones/07-cierre-paso-1.md` y `docs/diseno-estudio-2.md`
solo en lo que se dice aqui. Si alguna candidata pasa, nada de esto aplica: va al papel (`11-papel.md`).

## 12.1 Por que

Mirada la reserva, todo 2001-2026 queda visto: una idea nueva probada ahi "saldria bien" con facilidad, porque se
elegiria sabiendo que funciono. Esperar 2-3 anyos de datos nuevos en papel no le sirve al propietario. Queda un
periodo que nadie ha mirado: **antes del anyo 2000**.

## 12.2 Si no pasa ninguna (A): se permite un estudio 3, con estas reglas

1. **Un enfoque distinto**, escrito y subido a git **antes** de bajar o mirar ningun dato de antes del 2000.
2. **Se prueba solo con datos anteriores al 2000** (indices de bolsa, bonos y oro, con costes e impuestos puestos a
   mano; los ETF de hoy no existian). Que datos gratuitos hay, **sin comprobar**: se verifica antes de disenyar.
3. **Liston mas alto que el del estudio 2**, fijado antes de medir, que cuente **todos** los intentos hechos hasta
   entonces (5 del estudio 1 y 2 del estudio 2).
4. Es la ultima reserva limpia del pasado: si el estudio 3 tampoco pasa, se aplica 12.3 sin mas estudios sobre el
   pasado.

## 12.3 Red de seguridad (C): Ebisu como bot del indexado

Si no hay estrategia ganadora, Ebisu puede seguir como un bot que **automatiza el indexado mantenido**: compra el
indexado mundial, lo mantiene, informa por Telegram y no hace nada mas (sin vender por senyales ni anyadir riesgo).
No pretende ganar al indice: lo iguala, menos sus costes. Se construye solo si el propietario lo decide entonces.
