# Revision de los 3 dias del bot en papel (preparada el 17/10/2026, para el 18/10/2026)

Plan: `docs/plan-bot-papel.md` (seccion 10: "3 dias sin incidencias antes de la primera senyal real") y
`docs/instalacion-bot.md`. El bot da la vuelta del dia desde el 15/10/2026 (instalado ese dia).

## Como se hace (5 minutos)

1. **Informe automatico en el VPS** (solo lee; no cambia nada ni avisa a nadie):

   ```
   sudo bash /opt/ebisu/deploy/revision.sh 2026-10-15
   ```

   Ensenya: el commit que corre (0), las vueltas de cada dia (1), los avisos de Telegram (2), los precios y sus huecos
   (3), la salud que apunta la vuelta (4), lo que haria la regla hoy (5), los servicios y los errores del registro (6),
   las copias del VPS (7) y la **prueba de oro** con precios reales de hoy (8: el papel del bot tiene que dar exactamente
   lo mismo que el simulador del estudio 4).
2. **A mano** (el propietario): Healthchecks (`ebisu-dia`, `ebisu-copia` y `ebisu-copia-portatil` en verde), los mensajes
   de Telegram de estos dias y el panel.
3. **En el portatil:** `var/copia-ebisu.log` (una copia buena cada dia).

## Que cuenta como incidencia

**Grave** (con una sin resolver no se empieza el papel): las mismas que el juez del bot (`ebisu/juez.py`) mas las del
funcionamiento diario.

- Un dia sin ninguna vuelta buena, o una vuelta fallida.
- Un aviso de precios de tipo salto raro (> 15 % en un dia) o pieza sin precio nuevo en 3 dias habiles.
- Avisos que no se pudieron enviar por Telegram.
- La IA no responde (version distinta de la verificada) o el latido no llega a Healthchecks.
- La prueba de oro no coincide con el simulador.
- Un servicio de Ebisu parado o reiniciandose sin parar.

**Leve** (se anota; no impide empezar si esta entendido y resuelto): un dia que llega tarde, una revision de la fuente,
un cierre ajustado distinto, un corte breve de conexion con Telegram que el bot supera solo.

## Lo que ya se sabe (17/10/2026)

| Dia | Que paso | Gravedad | Estado |
|---|---|---|---|
| 15/10 | Antes de rellenar el `.env`, `ebisu-comandos` se reiniciaba sin token (esperado en la instalacion) | - | Resuelto el 15/10 |
| 16/10 | 4 avisos "14/10 llega despues del 15/10" (Yahoo no dio el 14/10 en el primer relleno) | Leve | Resuelto: antes del papel se rellenan los dias que faltan (commit `d69a21e`); el 14/10 ya esta |
| 16/10 | Copia del portatil: falso aviso a las 12:00 | Leve (no es del bot) | Resuelto: fallo del script (commit `f6c4714`) |
| 16/10 | Dos cortes breves de conexion con Telegram en `ebisu-comandos` | Leve | Lo supero solo, sin reiniciarse |

Cambios de codigo en estos dias: la cache de yfinance, el relleno de huecos, el panel nuevo y la salud. **Ninguno toca
la estrategia** (`ebisu/estrategia.py`, cuya huella se fija al empezar).

## La decision del propietario

Si el informe y lo que se mira a mano estan bien:

- **Empezar el papel con la senyal de octubre** (la primera con todo listo, P5):

  ```
  sudo -u ebisu bash -c 'cd /opt/ebisu && .venv/bin/python -m ebisu.dia --empezar 2026-10-30'
  ```

  (30/10/2026 es el ultimo dia habil de octubre). Fija la primera senyal y la huella de la estrategia **una sola vez**.
- **Que pasa despues:** el 30/10, al cerrar, la vuelta calcula la senyal y la IA la explica (en sombra); el lunes
  02/11 se ejecuta en papel (operaciones y resumen del mes por Telegram); desde ese domingo, el "todo bien" semanal. El
  papel dura 6 revisiones (decision 11) y pasa solo con las cuatro condiciones de 11.2.

Si hay algo grave: se arregla y se cuentan de nuevo 3 dias sin incidencias (si da tiempo, aun con la senyal del 30/10;
si no, la de noviembre, el 30/11/2026). **No se rellena hacia atras** (P5).
