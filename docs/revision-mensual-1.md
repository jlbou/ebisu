# Primera revision mensual del papel (30/11/2026): guia (preparada el 26/11/2026)

Parte de `docs/decisiones/11-papel.md` (que tiene que cumplir el papel) y de `docs/revision-3-dias.md` (como se revisa).
**Las cifras de abajo son del 26/11/2026, con precios hasta el 25/11; la revision real las vuelve a medir.**

## Que es esta revision

La segunda senyal de H1-M (la de fin de mes). Es la primera de las 6 revisiones del papel (decision 11.1: 6 meses):
30/10 (primera senyal, ya hecha), **30/11**, 31/12, 29/01, 26/02 y 31/03. El 30/11 el bot calcula la senyal al cerrar, la IA
la explica en sombra y el lunes 01/12 se ejecuta en papel.

## Como esta el papel (26/11, sin revisar a mano)

| | |
|---|---|
| Valor en papel | 247,53 € (de 250 €) |
| Si vende hoy | 247,29 € |
| Caida maxima hasta ahora | 0,99 % (limite: 14,9 %) |
| Referencia (indexado mantenido) | 234,26 € |
| Operaciones | una sola tanda: 02/11 (compra bolsa y bonos a 1/6 cada uno) |
| Vueltas del dia | 27 seguidas bien (30/10 a 25/11), 0 fallidas |
| Prueba de oro (papel = simulador) | OK |
| Incidencias abiertas | ninguna; el informe cuenta 1 "grave" por las 6 vueltas fallidas del 18/10 (resuelto y anotado) |

## Que haria la regla hoy (precios del 25/11, no es la senyal)

| Pieza | Medias superadas | Peso |
|---|---|---|
| Bolsa | 0 de 4 | 0 % |
| Bonos | 3 de 4 | 25 % |
| Oro | 0 de 4 | 0 % |
| Monetario | | 75 % |

Si el 30/11 sigue asi, la senyal **vende la bolsa** (de 16,7 % a 0 %) y sube los bonos (de 16,7 % a 25 %), y el resto va
al monetario. **Es lo que diria hoy, no una promesa**: manda el cierre del 30/11.

## Que se mira ese dia

1. **Informe del VPS:** `sudo bash /opt/ebisu/deploy/revision.sh 2026-10-15` (solo lee; se lanza por SSH al VPS, cuyo
   alias esta en las notas privadas). Esperado: 0 graves nuevos (el del 18/10 sigue contando por historial).
2. **Las cuatro condiciones de la decision 11.2:**
   - **Fidelidad:** la prueba de oro sigue en OK (papel = simulador).
   - **Sin incidencias graves sin resolver:** vueltas del 30/11 y 01/12 buenas, sin precios con salto ni sin cierre.
   - **Caida:** por debajo del 14,9 % (hoy 0,99 %).
   - **Decision del propietario:** solo al final del papel (marzo/abril de 2027), no en cada revision.
3. **A mano:** Healthchecks (`ebisu-dia`, `ebisu-copia`, `ebisu-copia-portatil` en verde), los mensajes de Telegram
   (senyal, operaciones y resumen del mes) y el panel.
4. **La IA en sombra (decision 11.3):** el 30/10 propuso frenar la bolsa por la ola de ventas en tecnologicas e IA. Se
   compara con lo que hizo la bolsa mientras duro el freno (si bajo, acerto; si subio, fallo). Hace falta **al menos 5
   casos**; hoy hay 1. No se evalua el acierto a mano: lo calcula el panel; hay que leerlo.

## Cuando hay algo grave

Se arregla y se cuenta de nuevo (como el 18/10). **No se rellena hacia atras** (P5). Una incidencia grave sin resolver
impide dar el papel por bueno.

## Recordatorio de calendario

- 29/11 (domingo): "todo bien" semanal por Telegram (el cuarto).
- 30/11: senyal. 01/12: operaciones en papel.
- **VPS pagado hasta ~abril de 2027:** hablar antes del final del papel (31/03).
