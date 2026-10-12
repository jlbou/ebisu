# Ebisu

Bot de trading **sin apalancamiento** con activos que no son cripto: bolsa, bonos y oro, siguiendo la tendencia.
Proyecto personal, en construccion. **No es asesoramiento financiero.**

## Por que va al reves

El primer bot del autor (cripto) construyo toda la infraestructura antes de tener una estrategia con ventaja, y
despues de ~30 estudios ninguna estrategia activa ganaba. Ebisu sigue el orden contrario:

1. **Decisiones de fondo** (mercado, capital, apalancamiento, vehiculo, objetivo): [`docs/prd-paso-1.md`](docs/prd-paso-1.md)
   y cada una en [`docs/decisiones/`](docs/decisiones/). **Hecho.**
2. **Estrategia probada con la historia**, con el criterio fijado y subido a git **antes** de medir: exploracion,
   reserva sin mirar (una sola vez) y un liston contra la suerte por el numero de variantes probadas
   ([`docs/hipotesis.md`](docs/hipotesis.md)). **En curso.**
3. **Solo si alguna estrategia pasa**, construir el bot.

Si ninguna pasa, la conclusion es mantener un fondo indexado, sin bot.

## Reglas que no cambian

- Sin apalancamiento (1x): ni CFD, ni futuros, ni margen.
- La IA explica y puede frenar una compra; nunca comprar ni anyadir riesgo.
- Las claves, solo en un `.env` local que nunca entra en git.

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
