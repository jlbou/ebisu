# H2 en la reserva de divisas: criterio fijado ANTES de medir (13/10/2026)

Pedido por el propietario (opcion B) tras el estudio 2. Se fija y se sube a git antes de medir; desde ese commit no se
cambia nada.

## Que se prueba

- **H2 tal cual** esta definida en `docs/diseno-estudio-1.md` y programada en `estudios/estudio1/h2.py` (rango del dia
  anterior en los 7 pares principales, datos de Dukascopy, sin apalancamiento), sin tocar ni un parametro.
- **Tramo: la reserva de divisas, 2015-01-01 a 2026-09-30.** Las divisas de ese tramo no se han mirado nunca: el
  estudio 1 solo midio 2003-2014 y el estudio 2 solo midio bolsa, bonos y oro. Se mide **una vez**.
- Referencia: la del estudio 1 (indexado mantenido, `referencia()` del estudio 1).

## Cuando pasa (todas)

1. Gana a la referencia, o casi la iguala con claramente menos caida (condicion 1 de siempre).
2. No pierde: TAE neta > 0.
3. **Sharpe probabilistico contra 0 >= 0,99.** Mas alto que el 0,95 del estudio 2, como pide la decision 12: es el
   octavo intento (5 del estudio 1 y 2 del estudio 2); con una correccion de Bonferroni sobre 8 intentos y un 10 % de
   error total sale 1 - 0,10/8 = 0,9875, que se redondea a 0,99.
4. Las dos de H2 del estudio 1: intervalo del 90 % del resultado por operacion > 0, y positiva en >= 5 de los 7 pares.

## Que se sabe antes de medir (y que no cambia nada)

- En la exploracion 2003-2014, H2 perdio un 3,94 % al anyo con una caida del 38,7 %.
- La IA ya vio la reserva de bolsa, bonos y oro (estudio 2), no la de divisas.
- La version programada es la que el propietario explico de la idea de una persona conocida; no se sabe si esa persona
  opera exactamente asi (pares, horario, stops, apalancamiento). Lo que se mide es esta version.

## Si pasa / si no pasa

- **Si pasa:** no va directamente al papel. Antes, el propietario decide (decision 5: sin apalancamiento) y se
  comprueba que Trading 212 deja operar divisas sin CFD; sin comprobar.
- **Si no pasa:** H2 queda descartada del todo; se vuelve a la decision pendiente (cerrar Ebisu como bot, estudio 3 o
  pausa). La version de la persona conocida, si es distinta, solo se podria probar con datos que no sean 2003-2026.

## Despues: el orden real de las horas (13/10/2026, SOLO INFORMACION; opcion A del propietario)

Tras el veredicto se vio que en el ~23 % de las compras el mismo dia se toca tambien el maximo de ayer, y el criterio
contaba lo peor. Se calcula H2 con las velas de 1 hora (`estudios/h2reserva/h2_horas.py`, en 2003-2014 y 2015-2026)
**solo como informacion**: los dos tramos ya estan vistos, asi que **no cambia ningun veredicto** y H2 no puede ir a
dinero real por este calculo. Si sale claramente negativa, la idea queda cerrada; si sale positiva, lo unico limpio
seria probar las reglas exactas de la persona conocida hacia adelante. Escrito antes de calcularlo.
