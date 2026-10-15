# Instalacion del bot en papel en el VPS (INSTALADO el 15/10/2026, commit ba59bea)

Plan: `docs/plan-bot-papel.md` (P2, P6 y seccion 10). Ficheros: `deploy/`. Ploutos no se toca en ningun paso.

## Antes (lista de comprobacion, skill `engineering:deploy-checklist`)

- [x] Pruebas en verde en el portatil y en GitHub (hay que **subir los commits a GitHub**: el VPS baja el codigo del
      repositorio publico, a un commit concreto).
- [x] Revision de seguridad hecha (seccion de abajo).
- [x] El propietario crea en Healthchecks.io una comprobacion **nueva, solo de Ebisu** (periodo 1 dia, gracia 4 h).
- [x] El propietario genera el token de la IA para Ebisu (`claude setup-token`).

## Instalar (con el propietario)

1. `sudo bash instalar.sh <commit> <usuario-admin>` en el VPS (crea el usuario `ebisu`, `/opt/ebisu`, el entorno con
   las versiones exactas de `deploy/requirements-bot.lock`, la copia propia de la IA, los servicios, y hace la prueba
   en seco).
   **La IA, copia propia (decision del propietario del 15/10/2026, opcion A):** la del VPS es de Ploutos (vive en
   `/home/ploutos`, que los servicios de Ebisu no pueden ver). `deploy/instalar-ia.sh` (lo lanza `instalar.sh`) baja la
   version verificada de la web oficial, la comprueba contra el manifiesto firmado y la deja en `/opt/ebisu/bin`, de
   root y solo lectura para el bot. Ploutos no se toca.
2. El propietario rellena `/opt/ebisu/.env` (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, HEALTHCHECK_EBISU,
   CLAUDE_CODE_OAUTH_TOKEN; permisos 600) y vuelve a lanzar `instalar.sh`.
3. Un mensaje de prueba por Telegram, un latido de prueba y `/estado`.
4. En el portatil: `.\deploy\instalar-tarea-copia.ps1` (la copia diaria, 7 dias).
5. **3 dias sin incidencias**; despues, `--empezar` con la primera senyal (la del 30/10/2026 si da tiempo).

## Estado (15/10/2026)

- Instalado con `instalar.sh ba59bea root` (el usuario admin del VPS es root). Prueba en seco: OK (150 titulares).
- `.env` del VPS: solo las 4 claves, de `ebisu` y permisos 600 (el mismo fichero que en el portatil).
- Probado dentro del aislamiento de los servicios: mensaje de Telegram, latido de Healthchecks (en verde), IA propia
  2.1.266, y `/estado` responde. Ploutos sigue con sus 8 servicios.
- **La IA, con una pregunta de verdad** (15/10, una llamada de la cuota, con datos de prueba): dentro del aislamiento
  exacto de `ebisu-dia.service` (incluido `PrivateTmp=true`, que la IA necesita para escribir en `/tmp`, y
  `MemoryMax=600M`): respuesta valida en 5,2 s; el proceso mas grande, **224 MB** (en Ploutos se midieron 380-410 MB
  en el portatil). Cabe de sobra: el limite no se toca.
- Copias: `ebisu-copia.service` probado en el VPS; la tarea del portatil registrada y probada (resultado 0).
- El panel se abre por Tailscale en el puerto 8611, por IP o por el nombre de la maquina (MagicDNS; el panel se lo
  pregunta a Tailscale al arrancar, no se escribe en ningun fichero).
- Siguiente: **3 dias sin incidencias** (hasta el 18/10/2026) y despues `--empezar` (decide el propietario).

## Healthchecks: tres comprobaciones de Ebisu (decision del propietario, 15/10/2026)

Coordinadas con las de Ploutos (mismo canal de avisos, nombres `ebisu-...`, etiqueta `ebisu`):

| Comprobacion | La late | Clave y donde va | Periodo / gracia |
|---|---|---|---|
| `ebisu-dia` | la vuelta del dia (VPS) | `HEALTHCHECK_EBISU`, solo en el `.env` del VPS | 1 dia / 4 h |
| `ebisu-copia` | `copia-vps.sh` (VPS, 23:30); `/fail` si falla | `HEALTHCHECK_EBISU_COPIA`, solo en el `.env` del VPS | 1 dia / 4 h |
| `ebisu-copia-portatil` | `copia-diaria.ps1` (portatil); `/fail` si falla | `HEALTHCHECK_EBISU_COPIA_PORTATIL`, solo en el `.env` del portatil | 1 dia / 1 dia |

**Cada URL solo en la maquina que late** (leccion de Ploutos): si el portatil tuviera una URL del VPS, podria latir en
su nombre y tapar una caida. El portatil se queda sin `HEALTHCHECK_EBISU` ni el token de la IA (no los usa).
No se vigila `ebisu-comandos` (solo `/estado` y `/detalle`; systemd lo reinicia). Si cae el VPS entero, avisan a la
vez las de los dos bots: eso ya dice que es el servidor.

## Vuelta atras

`sudo bash desinstalar.sh` (para y quita solo los servicios de Ebisu); con `--borrar`, tambien `/opt/ebisu` y las
copias (pide escribir BORRAR).

## Revision de seguridad (15/10/2026)

La skill `security-review` no pudo arrancar (pide una rama remota que este repositorio no tiene configurada); revision
hecha a mano con sus mismos puntos:

| # | Punto | Estado |
|---|---|---|
| S1 | Secretos: solo en `.env` (600); el bot lee 4 claves, nunca las de Trading 212; tapados en todo error y registro | OK (pruebas) |
| S2 | La IA no hereda ninguna clave; sin herramientas; titulares como datos delimitados; salida validada y limpiada | OK (pruebas) |
| S3 | XML de fuera: sin DOCTYPE/ENTITY, tamanyo maximo, texto plano | OK (pruebas) |
| S4 | Panel: solo Tailscale; sin rutas a ficheros; CSP; botones con cabecera y Origin | OK (pruebas) |
| S5 | **DNS rebinding** (una web de fuera apunta su dominio a la IP del panel y pasa la comprobacion del Origin, porque Origin y Host coinciden): **corregido**, el panel solo responde si la cabecera Host es la suya. **El mismo hueco esta en el panel de Ploutos** (`api/mando.py`), que no se ha tocado | Corregido |
| S6 | Longitud del cuerpo invalida o negativa en el panel | Corregido |
| S7 | Dependencias: fijadas todas, tambien las indirectas (`deploy/requirements-bot.lock`) | OK |
| S8 | Servicios aislados: usuario propio, solo escriben en su `var/`, `/opt/ploutos` inaccesible | OK (prueba de los ficheros) |
| S9 | Repositorio publico: sin IP, nombres de maquina ni secretos en `deploy/` | OK (prueba) |
