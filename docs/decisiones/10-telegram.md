# Decision 10: Telegram (en curso desde el 12/10/2026; solo disenyo, se construye si una estrategia pasa)

El bot de Telegram lo crea el propietario con @BotFather; el token va solo en su `.env` (`TELEGRAM_TOKEN`).
En los mensajes, en castellano, "la IA", nunca "Claude".

## 10.1 Que mensajes llegan (opcion B, 12/10)

Disenyo que sirve gane la variante que gane (mensual, semanal o diaria):

| Tipo | Cuando |
|---|---|
| Operaciones | Solo cuando el bot compra o vende algo; si una revision no cambia nada, no escribe. Si gana H2 (diaria): un resumen diario agrupado, no un mensaje por operacion |
| Resumen mensual | Una vez al mes: valor, frente al indexado y la explicacion de la IA |
| **"Todo bien" semanal** | **Una vez por semana**, corto, aunque no pase nada (eleccion del propietario: saber que el bot esta vivo) |
| La IA frena una compra | Cuando pasa: que freno y por que |
| Aviso de incidencia | Cuando pasa: sin precios, broker desconectado, orden no ejecutada, bot parado |
| El bot se aleja del criterio | Cuando pasa: en papel va peor de lo que decia el estudio |
| Recordatorio de la renta | Una vez al anyo, en abril, con el resumen fiscal |

## 10.2 Comandos (opcion A, 12/10)

| Comando | Que hace |
|---|---|
| `/estado` | Responde con el resumen: valor, piezas, proxima revision y salud |
| `/pausa` | Sin compras nuevas; lo que hay se mantiene y se sigue vendiendo si la regla lo dice |
| `/reanudar` | Quita la pausa, con confirmacion (`/si` en 60 s), como en Ploutos |
| `/detalle` | La version larga (anyadido el 12/10, ver 10.3) |

**Fuera a proposito:** vender todo desde el movil (un error de dedo o el panico en una caida es lo que el bot debe
evitar; si hace falta, en la app del broker) y ordenes de compra manuales (el bot sigue la regla). Solo responde al
chat del propietario (`TELEGRAM_CHAT_ID`).

## 10.3 Formato de los mensajes (opcion A, 12/10)

- **Corto, las cifras primero y la IA en una o dos frases.** Resumen mensual: valor, frente al indexado, peor caida,
  las piezas con sus puntos (medias superadas) y pesos, la IA y la proxima revision. Operaciones: vendido, comprado,
  coste y ganancia realizada. "Todo bien" semanal: una linea.
- **`/detalle`** (pedido por el propietario): la version larga bajo demanda. Un grafico (imagen) del valor frente al
  indexado y de cada pieza con sus 4 medias; la explicacion completa de la IA; las operaciones del mes; y Hacienda del
  anyo (ganancias, perdidas y lo que tocaria pagar).

## Cambio del 14/10/2026 (plan del bot en papel, P4)

En Telegram solo quedan `/estado` y `/detalle`. **`/pausa` y `/reanudar` se quitan de Telegram y pasan al panel** (decision del propietario), que solo se ve por Tailscale. En papel la pausa no actua; se activa con dinero real. Ver `docs/plan-bot-papel.md` 9.
