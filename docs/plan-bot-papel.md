# Plan del bot en papel (H1-M): todo antes de programar (14/10/2026, BORRADOR para el propietario)

Paso 3 de Ebisu tras la decision 15 (`docs/decisiones/15-aceptar-h1.md`). Skills usadas: `anthropic-skills:superpowers`
(entender, planificar, criterios, revision), `ml4t-production-readiness` (las cinco capas antes de operar),
`engineering:system-design` (componentes, flujo de datos, fallos). Se ha leido, sin tocar nada, Ploutos: su "papel de
L" (`scripts/papel_l.py`), Telegram (`notify/`), la IA (`ai/invoke.py`, `deploy/install-claude.sh`) y sus servicios.
**No se programa nada hasta que el propietario apruebe este plan.**

## 1. Que se pide

- Un bot que lleve **H1-M en papel durante 6 meses** (decision 11: ~6 revisiones), con precios reales de los 4 ETF
  (VWCE, CEMF, SGLD, XEON), sin dinero ni ordenes reales.
- Que el propietario **no tenga que hacer nada** (decision 6) y sepa por Telegram lo que pasa (decision 10).
- La IA explica cada mes y dice si frenaria una compra, **en sombra**: el bot no le hace caso (decisiones 8 y 11.3).
- Al final, el papel pasa si cumple la decision 11.2: fidelidad al simulador, sin incidencias graves, no caer mas que
  la peor caida historica (**14,9 %**, estudio 4) y el si del propietario.

## 2. Supuestos y lo que falta

- [Supuesto] Empieza con la senyal del ultimo dia habil de **octubre de 2026** y acaba con la de **abril de 2027**.
- [Supuesto] 250 € de papel (los tramos de impuestos se calculan sobre esa cifra, como en el estudio).
- Decisiones del propietario pendientes: seccion 9 (P1-P5).

## 3. Como funciona (una vez al dia, sin estado que importe)

Como el papel de L en Ploutos: **cada dia rehace el papel entero desde el primer dia con el MISMO simulador que se
midio** (`estudios/estudio4/simulador4.py`, copiado al bot sin cambiar la logica). Asi no hay una "cartera" que se
pueda corromper: todo sale de los precios guardados.

```
20:00 (Madrid), dias habiles:
  1. Precios: baja el cierre de los 4 ETF  ->  comprueba (fecha de hoy, sin huecos, saltos raros)  ->  los guarda
     una sola vez (un precio guardado no se cambia: si la fuente lo revisa despues, se cuenta y se avisa)
  2. Papel: simulador4 desde el inicio hasta hoy con los precios guardados  ->  operaciones, valor, caida
  3. Compara con lo de ayer: hay operacion nueva?  ->  Telegram (decision 10.1)
  4. Si hoy es la senyal del mes: la IA (sombra)  ->  explicacion + "frenaria o no" (JSON fijo)  ->  se guarda
  5. Juez del papel: caida <= 14,9 %, ninguna revision saltada, precios al dia  ->  si falla, aviso de incidencia
  6. Latido: "todo bien" el domingo; resumen el mes; recordatorio de la renta en abril
```

## 4. Piezas y de donde salen

| Pieza | Que hace | Origen |
|---|---|---|
| `ebisu/precios.py` | Baja y valida los cierres; guarda sin sobrescribir | Nuevo (yfinance, ya en las dependencias) |
| `ebisu/estrategia.py` | H1-M: senyal, pesos, impuestos y costes | **Copia exacta** de `simulador4.py` (una prueba compara las dos) |
| `ebisu/papel.py` | Rehace el papel y saca operaciones, valor y caida | Idea de `papel_l.py` de Ploutos |
| `ebisu/juez.py` | Las condiciones de la decision 11.2 | Nuevo |
| `ebisu/noticias.py` | Lee los RSS cada dia y guarda los titulares nuevos | Copia adaptada de `data/medios/rss.py` de Ploutos |
| `ebisu/ia.py` | Llama a `claude -p` sin herramientas, sin ver claves, con salida JSON; si falla, nada | Copia adaptada de `ai/invoke.py` y `ai/parser.py` de Ploutos |
| `ebisu/latido.py` | Latido diario a Healthchecks.io; nunca lanza; la URL es secreta | Copia de `notify/latido.py` de Ploutos |
| `ebisu/telegram.py` | Envia mensajes; el token nunca sale en un error; si falla, no tumba nada | Copia de `notify/telegram.py` de Ploutos |
| `ebisu/mensajes.py` | Los textos de la decision 10 ("la IA", nunca "Claude") | Nuevo, con el formato de 10.3 |
| `ebisu/reglas.py` | Reglas duras | Nuevo (seccion 5) |
| `deploy/` | Servicio y temporizador diario (systemd), instalacion | Adaptado de los de Ploutos |

## 5. Reglas duras (en el codigo, con pruebas)

1. **En papel no existe ningun modulo de ordenes** ni clave de Trading 212 que pueda operar.
2. Solo los 4 ISIN de la lista (IE00BK5BQT80, IE000K1VI152, IE00B579F325, LU0290358497); **nunca CFD**.
3. Suma de pesos <= 1 (sin apalancamiento); ninguna pieza por encima de 1/3.
4. La IA **no cambia nada** del papel (sombra); su salida invalida o tardia = no hacer nada.
5. La IA nunca ve claves ni variables de entorno (como la regla 19 de Ploutos); sin herramientas.
6. Secretos solo en `.env` (token de Telegram, chat y token de la IA), puestos por el propietario.

## 6. Lo que puede fallar y que hace el bot (production-readiness)

| Fallo | Respuesta |
|---|---|
| La fuente no da el precio de hoy | Reintenta 3 veces; si no, aviso de incidencia; el dia de la senyal, la senyal se aplaza al siguiente dia con precio (como haria el simulador con el ultimo dia habil con datos) y se avisa |
| Un precio raro (salto > 15 % en un dia) | No se guarda; aviso; se decide a mano |
| La fuente cambia un precio pasado | Manda el guardado; se cuenta y se avisa |
| Telegram caido | Se guarda en una cola y se reenvia (como el `outbox` de Ploutos) |
| La IA no responde, o el token caduca | No pasa nada en el papel; aviso |
| El VPS se reinicia o el servicio no corre un dia | El dia siguiente lo rehace todo; el juez avisa si falta una revision |
| La caida pasa del 14,9 % | Aviso inmediato: el papel no pasa (11.2.3) |

## 7. Criterios de calidad (antes de instalar)

- Pruebas con datos inventados: la copia de la estrategia da **exactamente** lo mismo que `simulador4.py`; el papel
  rehecho dos veces da lo mismo; un precio que falta o un salto raro dan aviso; Telegram caido no tumba el bot; la IA
  con salida mala o lenta no cambia nada; las reglas duras se cumplen (prueba que intenta romperlas).
- **Prueba en seco** con los precios reales (sin Telegram ni guardar), como `--seco` en Ploutos.
- `ruff` y `pytest` en verde; lista de comprobacion de la instalacion (skill `engineering:deploy-checklist`).
- Incompleto si: falta cualquier mensaje de la decision 10.1 que aplique al papel, o la prueba de fidelidad.

## 8. Orden de construccion

1. Precios (y la eleccion de fuente, P1). 2. Estrategia copiada + prueba de igualdad. 3. Papel y juez. 4. Telegram y
mensajes. 5. IA en sombra. 6. Servicio diario, prueba en seco e instalacion en el VPS. Cada paso con sus pruebas y con
el OK del propietario.

## 9. Decisiones del propietario (una por mensaje)

| # | Cuestion |
|---|---|
| P1 | **Decidido (14/10, opcion A): la senyal sobre los precios reales de los 4 ETF en Yahoo**, con los controles de la seccion 6; si Yahoo da problemas, se anyade una segunda fuente (opcion C). Comprobado: VWCE.DE, CEMF.DE (desde el 04/08/2025: 305 dias, bastan para la media de 200), SGLD.MI y XEON.DE, todos hasta el 14/10/2026 |
| P2 | **Decidido (14/10, opcion A): el mismo VPS que Ploutos, completamente aparte** (usuario `ebisu`, `/opt/ebisu`, entorno, `.env` y servicios propios; no toca ningun fichero ni servicio de Ploutos; usa el binario de la IA ya instalado solo para ejecutarlo, con configuracion propia). **Latido a Healthchecks.io** (copia de `notify/latido.py` de Ploutos): una comprobacion propia de Ebisu, que crea el propietario; su URL va en el `.env` de Ebisu. El latido se manda solo si la vuelta del dia acaba bien; si falta, Healthchecks avisa |
| P3 | **Decidido (14/10, opcion A): RSS de fuentes oficiales (comunicados del BCE y de la Fed) y de 3-4 medios economicos** (se eligen y se comprueba que funcionan al construir). Se recogen durante el mes y la IA los recibe el dia de la senyal como **texto no confiable** (nunca instrucciones); la IA no navega ni tiene herramientas. Pieza: copia adaptada de `data/medios/rss.py` de Ploutos |
| P4 | Que comandos de Telegram hacen falta en papel |
| P5 | El panel (decision 9): ¿ahora o despues del papel? |
