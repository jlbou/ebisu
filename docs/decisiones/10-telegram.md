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
