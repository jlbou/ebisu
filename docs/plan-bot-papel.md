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

- Empieza con la primera senyal mensual con todo listo (P5) y dura 6 revisiones.
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
| `ebisu/panel/` | El panel de la decision 9 (una pagina, 6 secciones), solo por Tailscale; pausa sin efecto en papel | Adaptado de `api/` y `ui/` de Ploutos |
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
mensajes. 5. IA en sombra. 6. Panel. 7. Servicios, prueba en seco e instalacion en el VPS. Cada paso con sus pruebas y con
el OK del propietario.

## 9. Decisiones del propietario (una por mensaje)

| # | Cuestion |
|---|---|
| P1 | **Decidido (14/10, opcion A): la senyal sobre los precios reales de los 4 ETF en Yahoo**, con los controles de la seccion 6; si Yahoo da problemas, se anyade una segunda fuente (opcion C). Comprobado: VWCE.DE, CEMF.DE (desde el 04/08/2025: 305 dias, bastan para la media de 200), SGLD.MI y XEON.DE, todos hasta el 14/10/2026 |
| P2 | **Decidido (14/10, opcion A): el mismo VPS que Ploutos, completamente aparte** (usuario `ebisu`, `/opt/ebisu`, entorno, `.env` y servicios propios; no toca ningun fichero ni servicio de Ploutos; usa el binario de la IA ya instalado solo para ejecutarlo, con configuracion propia). **Latido a Healthchecks.io** (copia de `notify/latido.py` de Ploutos): una comprobacion propia de Ebisu, que crea el propietario; su URL va en el `.env` de Ebisu. El latido se manda solo si la vuelta del dia acaba bien; si falta, Healthchecks avisa |
| P3 | **Decidido (14/10, opcion A): RSS de fuentes oficiales (comunicados del BCE y de la Fed) y de 3-4 medios economicos** (se eligen y se comprueba que funcionan al construir). Se recogen durante el mes y la IA los recibe el dia de la senyal como **texto no confiable** (nunca instrucciones); la IA no navega ni tiene herramientas. Pieza: copia adaptada de `data/medios/rss.py` de Ploutos |
| P4 | **Decidido (14/10): en Telegram solo `/estado` y `/detalle`** (en papel y despues). **Pausar y reanudar, desde el panel**, no desde Telegram (cambia la decision 10.2). En papel la pausa no actua (romperia la fidelidad, 11.2.1); se activa con dinero real. Escuchar comandos pide un segundo servicio (como `ploutos-telegram`). Piezas: copia adaptada de `notify/comandos.py` (solo esos dos) y de los controles del panel (`api/mando.py`: solo por Tailscale y con la cabecera contra otras paginas) |
| P5 | **Decidido (15/10, opcion A): el panel se construye antes de lanzar el papel**, con el disenyo de la decision 9, solo por Tailscale y con los botones de pausa visibles pero sin efecto en papel. El papel arranca con la primera senyal mensual en la que todo (panel incluido) este listo: la de octubre (30/10/2026) si da tiempo; si no, la de noviembre. **No se rellena hacia atras**: la IA en sombra no se puede hacer despues (ya sabria las noticias) |

## 10. Revision del plan (15/10/2026)

Skills: `engineering:testing-strategy` (piramide de pruebas), `engineering:deploy-checklist` (instalacion y vuelta
atras), `ml4t-production-readiness` y revision de seguridad propia. Lo de esta seccion **manda** sobre lo anterior.

### Correcciones tecnicas (aplicadas al plan)

| # | Agujero | Correccion |
|---|---|---|
| B1 | La fidelidad "por construccion" no prueba nada si el bot usa el mismo codigo | **Prueba de oro:** el papel del bot sobre los precios reales de los ETF 2020-2026 tiene que dar exactamente lo mismo que `simulador4.py` con esos precios; y una huella (hash) de `estrategia.py` guardada al empezar: si cambia durante el papel, es una incidencia |
| B2 | Cierre o cierre ajustado de Yahoo | Cierre (`Close`); los 4 son de acumulacion; se avisa si `Adj Close` difiere mas de un 0,1 % |
| B3 | Un precio de "hoy" provisional | Solo se guarda el cierre de un dia ya cerrado en su bolsa (despues de las 17:35) y con volumen > 0; reintentos hasta las 23:00 |
| B4 | El "todo bien" del domingo con un servicio solo de dias habiles | El temporizador corre todos los dias; fines de semana y festivos solo late y, el domingo, manda el "todo bien" |
| B5 | El binario de la IA es el de Ploutos: si Ploutos lo actualiza, cambia el de Ebisu | Ebisu comprueba la version al arrancar y, si no es la verificada, no llama a la IA y avisa. Token propio de Ebisu en su `.env` (lo genera el propietario) |
| B6 | Los titulares pueden llevar instrucciones o enlaces que la IA copie al mensaje | La salida de la IA se limpia antes de Telegram y del panel: sin enlaces, longitud maxima, HTML escapado y "Claude" -> "la IA" |
| B7 | Aislamiento de Ploutos | Usuario `ebisu` sin acceso a `/opt/ploutos`; servicios con `ProtectSystem=strict`, `ProtectHome`, `ReadWritePaths=/opt/ebisu/var`, limite de memoria (como Ploutos); puerto del panel distinto |
| B8 | Lo que no se puede rehacer (los precios tal como se vieron, el diario de la IA, los titulares) | Copia de seguridad diaria fuera del VPS (decision P6) |
| B9 | El repositorio es publico | Los ficheros de instalacion sin IP, nombres de maquina ni rutas personales: todo en el `.env` o en `CLAUDE.local.md` |
| B10 | El bot no necesita scikit-learn | `requirements-bot.txt` aparte (pandas, yfinance): menos memoria y menos superficie en el VPS |
| B11 | La referencia del resumen mensual | VWCE mantenido desde el primer dia del papel, con su gasto |
| B12 | Pruebas en GitHub sin red | Fuentes de precios, Telegram, IA y RSS simuladas en las pruebas |

### Piramide de pruebas

- **Unidad (muchas, rapidas):** validacion de precios, reglas duras (una prueba intenta romper cada una), limpieza de
  la salida de la IA, mensajes, comandos (solo el chat del propietario).
- **Integracion (algunas):** un dia completo con fuentes simuladas; el papel rehecho dos veces igual; Telegram caido,
  IA lenta o con salida mala, Yahoo sin precio, precio con salto raro: cada uno da su aviso y nada mas cambia.
- **Prueba de oro (B1)** y **prueba en seco** en el VPS con datos reales, sin Telegram ni guardar.
- **Instalacion:** lista de comprobacion (abajo) y vuelta atras.

### Lista de la instalacion (deploy-checklist)

- Antes: pruebas en verde en GitHub; revision del codigo; `.env` puesto por el propietario (permisos 600); copia de
  seguridad comprobada restaurando una vez.
- Instalar: usuario, carpeta, entorno, servicios; prueba en seco; un mensaje de prueba a Telegram; un latido de prueba.
- Despues: 3 dias sin incidencias antes de la primera senyal real del papel.
- **Vuelta atras:** parar y deshabilitar los servicios de Ebisu y borrar `/opt/ebisu`; Ploutos no se toca en ningun paso.

### Decision pendiente

| # | Cuestion |
|---|---|
| P6 | **Decidido (15/10, opcion A): copia diaria al ordenador del propietario** con una tarea programada propia de Ebisu (copia adaptada de `deploy/daily-backup.ps1` de Ploutos: por SSH, reintentos cada hora hasta que salga bien, aviso por Telegram si falla). **Se guardan solo las copias de los ultimos 7 dias**; las mas antiguas se borran. La tarea la aprueba e instala el propietario |

## 11. Construccion

- **Paso 1 (15/10): precios** (`ebisu/precios.py`, 8 pruebas). Hallazgo: Yahoo da a veces la fila del dia sin cierre
  aunque la bolsa ya haya cerrado; se salta y se vuelve a pedir.
- **Paso 2 (15/10): estrategia** (`ebisu/estrategia.py`, copia exacta de `simulador4.py`; prueba que compara el codigo
  y el resultado; huella SHA-256 en `ebisu/papel_huella.py`). **Configuracion de H1-M en el bot: sin gasto extra**,
  porque los precios de los ETF ya lo llevan descontado (en el estudio se sumaba porque las series eran indices); los
  costes del 0,10 % por lado siguen.
- **Paso 3 (15/10): papel y juez** (`ebisu/papel.py`, `ebisu/juez.py`, 10 pruebas; skills `python-testing`,
  `python-patterns` y `code-review`). El papel empieza el dia de ejecucion de la primera senyal, en el monetario.
  **Prueba de oro con precios reales** (`python -m ebisu.prueba_oro`, primera senyal 30/06/2026, hasta el 13/10/2026):
  valor diario, liquidacion y numero de operaciones **identicos** al simulador del estudio 4.
  Revision del codigo: (R1, corregido) si una pieza llega tarde, el papel no pasa del ultimo dia con las 4 piezas
  (antes rellenaba con el cierre de ayer y la senyal del mes podia salir con un precio viejo); (R2, se deja) si la
  estrategia no pudiera comprar por falta de caja, el juez lo veria como incidencia de coherencia: es lo que se quiere.
- **Revision del codigo de los pasos 1 y 2 (15/10, skills `python-patterns`, `python-testing` y `code-review`):**
  - (C1, corregido) Un dia sin cierre se saltaba y se guardaba el siguiente; si el que faltaba llegaba despues,
    cambiaba el pasado del papel (podia ser el dia de la senyal). Ahora, con precios ya guardados, se anyade solo
    despues del ultimo y en orden: un dia sin cierre corta la vuelta (aviso "hueco", se vuelve a pedir) y un dia
    anterior que llega tarde no se guarda (aviso "tarde"). En el primer relleno, los huecos antiguos se saltan.
  - (C2, corregido) Un volumen vacio se guardaba como "nan" y no contaba para el aviso de sin volumen: ahora es 0.
  - (C3, corregido) La escritura del CSV era fila a fila: ahora es una sola escritura, llevada a disco (`fsync`),
    para que un corte no deje una linea a medias.
  - (C4, corregido) Cada dia bajaba todo desde 2019: ahora, tras el primer relleno, solo los ultimos 15 dias.
  - Paso 2 sin hallazgos: la copia de la estrategia y la huella estan cubiertas por sus pruebas.
- **Paso 4 (15/10): avisos** (`ebisu/secretos.py`, `telegram.py`, `cola.py`, `latido.py`, `noticias.py`,
  `mensajes.py`; 13 pruebas sin red; skills `python-testing`, `python-patterns` y `code-review`). Telegram, cola y
  latido, copias adaptadas de Ploutos. Fuentes de noticias comprobadas el 15/10 (todas responden): BCE, Fed, FT
  (mercados), CNBC (finanzas), MarketWatch y Expansion (mercados); prueba real: 150 titulares, sin errores.
  Los `.env` del bot solo leen TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, HEALTHCHECK_EBISU y CLAUDE_CODE_OAUTH_TOKEN: las
  claves de Trading 212 que haya en el `.env` no se leen nunca en papel (regla dura 1).
  Revision: (N1, corregido; el mismo fallo esta en Ploutos) un titular con una etiqueta dentro (`<b>`) se cortaba en
  la etiqueta: ahora se lee todo el texto del elemento. Los mensajes llevan acentos (son para el propietario).
- **Paso 5 (15/10): la IA en sombra** (`ebisu/ia.py`, 12 pruebas con una IA inventada: nunca se llama a la real;
  skills `python-testing`, `python-patterns` y `code-review`). Copia adaptada de `ai/invoke.py` de Ploutos: entorno
  construido desde cero (solo su token), sin herramientas, sin sesiones, directorio vacio, stdin cerrado; version
  fijada a la verificada en Ploutos (2.1.266, por comprobar en el VPS). Contrato propio sin dependencias nuevas
  (Ploutos usa pydantic): `explicacion` (600 caracteres) y `frenos` (hasta 3, solo sobre piezas que se compran ese
  mes); cualquier otra cosa descarta la respuesta entera. Salida limpiada (B6) y diario de la IA para la decision 11.3.
