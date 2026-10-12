# Decision 11: el papel despues de la reserva (13/10/2026; fijado ANTES de medir)

Solo se llega al papel si una variante pasa la exploracion y la reserva. El papel no puede demostrar ventaja (con ~12
decisiones al anyo, ni un anyo la distingue de la suerte: eso lo decide el estudio); comprueba que **el bot hace lo
que decia el estudio** (precios, senyal, ordenes simuladas, mensajes y panel). Es papel propio: Trading 212 EU no
tiene cuenta demo.

## 11.1 Duracion (13/10)

| Variante ganadora | Revisa | Papel |
|---|---|---|
| H1-S | cada semana | **3 meses** (~13 revisiones) |
| H1-M, H1-MB, H1-F | cada mes | **6 meses** (~6 revisiones) |
| H2 | cada dia | por decidir |

## 11.2 Que tiene que cumplir el papel para pasar a dinero real (opcion A, 13/10)

Las cuatro, todas:

1. **Fidelidad:** con los mismos precios, el bot en papel toma **exactamente** las decisiones del simulador del estudio
   (fechas, pesos, compras y ventas). Si no coinciden, es un error del bot: se arregla antes de seguir.
2. **Sin incidencias graves sin resolver** (p. ej. una revision saltada por falta de precios o con el bot parado).
3. **No caer mas que la peor caida historica** de la variante (la mayor entre exploracion y reserva). Si cae mas, se
   para y se revisa.
4. **Decision expresa del propietario.** Aunque se cumpla todo, el dinero real solo con su si.

**Fuera, a proposito:** exigir que gane dinero en el papel. En 3 o 6 meses es sobre todo suerte; eso ya lo juzgo el
estudio con ~25 anyos de datos.

## 11.3 Como se juzga el freno de la IA, la hipotesis 4 (opcion A, 13/10)

- **En sombra** en el papel y despues con dinero real: la IA dice si frenaria o aplazaria una compra y por que; el bot
  **no le hace caso**. Cada caso queda registrado con su motivo.
- **Cada caso se compara** con lo que hizo la pieza durante el tiempo del freno: si bajo, el freno acerto; si subio,
  fallo.
- **El freno gana voz** (el bot le hace caso) solo con: **al menos 5 casos**, **acierto en la mayoria**, **de media
  evita perdidas** (no ganancias) y **decision expresa del propietario**. Hasta entonces, la IA solo explica.
- Se tiene en cuenta el veredicto de la fase 6 de Ploutos (si alli la IA aporto frente a la regla sola).
