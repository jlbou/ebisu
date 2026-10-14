# Prueba rapida del fixing (2020-2026): criterio fijado ANTES de medir (14/10/2026)

Opcion C del propietario: antes de construir el estudio completo, una sola medicion para saber si el patron de Krohn,
Mueller y Whelan sigue existiendo despues de su muestra (1999-2019). Si no llega al minimo, se para.

## Que se mide

- Pares: EUR/USD y USD/JPY (los unicos con un coste de ~1 pb por ida y vuelta; `docs/estudios/recerca-divisas-2.md`).
- Tramo: 2020-01-01 a 2026-09-30 (fuera de la muestra de los autores; con esos datos solo se han medido otras ideas).
- Datos: velas de 1 hora de Dukascopy, precio medio (bid + ask) / 2. Hora de Nueva York con su horario de verano.
- Rendimiento de la divisa extranjera contra el dolar (EUR/USD tal cual; USD/JPY con el signo cambiado).
- Ventanas (las del articulo, ajustadas a horas enteras y sin abrir entre las 16:00 y las 18:00, T3):
  - Tokio: antes = 18:00 a la hora del fixing (9:55 de Tokio: 20:00 en invierno de Nueva York y 21:00 en verano, el
    cierre de la vela que lo contiene); despues = del fixing a las 2:00.
  - Europa: antes = 2:00 a 8:00 (fixing del BCE a las 8:15, se toma el cierre de la vela de las 7:00); despues = 11:00
    (fixing de Londres) a 16:00.
- Reversion por dia y grupo = -(rendimiento antes) + (rendimiento despues). Cada grupo son dos operaciones (vender antes
  y comprar despues, en divisa extranjera), asi que **efecto por operacion = media diaria / 2**.
- Dias con todas las velas necesarias; fines de semana fuera.

## Cuando sigue (las dos cosas, en al menos uno de los 4 casos: 2 pares x 2 grupos)

1. Efecto por operacion >= **2,5 pb** (2,5 veces el coste de ~1 pb, regla de `ml4t-horizon-design`).
2. Estadistico t de la media diaria >= **2,5** (4 casos probados: liston mas alto que el habitual 2).

Si ninguno de los 4 cumple las dos, **se para** y no se hace el estudio completo. Si alguno cumple, solo dice que vale
la pena disenyar el estudio completo (con costes reales, el liston de riesgo M y una prueba limpia aparte).
