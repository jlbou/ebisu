# Instalacion del bot en papel en el VPS (15/10/2026, preparada; NO instalada)

Plan: `docs/plan-bot-papel.md` (P2, P6 y seccion 10). Ficheros: `deploy/`. Ploutos no se toca en ningun paso.

## Antes (lista de comprobacion, skill `engineering:deploy-checklist`)

- [ ] Pruebas en verde en el portatil y en GitHub (hay que **subir los commits a GitHub**: el VPS baja el codigo del
      repositorio publico, a un commit concreto).
- [ ] Revision de seguridad hecha (seccion de abajo).
- [ ] El propietario crea en Healthchecks.io una comprobacion **nueva, solo de Ebisu** (periodo 1 dia, gracia 4 h).
- [ ] El propietario genera el token de la IA para Ebisu (`claude setup-token`).

## Instalar (con el propietario)

1. `sudo bash instalar.sh <commit> <usuario-admin>` en el VPS (crea el usuario `ebisu`, `/opt/ebisu`, el entorno con
   las versiones exactas de `deploy/requirements-bot.lock`, los servicios, y hace la prueba en seco).
2. El propietario rellena `/opt/ebisu/.env` (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, HEALTHCHECK_EBISU,
   CLAUDE_CODE_OAUTH_TOKEN; permisos 600) y vuelve a lanzar `instalar.sh`.
3. Un mensaje de prueba por Telegram, un latido de prueba y `/estado`.
4. En el portatil: `.\deploy\instalar-tarea-copia.ps1` (la copia diaria, 7 dias).
5. **3 dias sin incidencias**; despues, `--empezar` con la primera senyal (la del 30/10/2026 si da tiempo).

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
