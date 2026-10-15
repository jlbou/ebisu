#!/usr/bin/env bash
# Copia diaria en el VPS (la lanza ebisu-copia.service). Guarda las 7 ultimas; el portatil las baja (copia-diaria.ps1).
# Sin el directorio de la IA (ia_config / ia_runtime): no hace falta y podria guardar estado de la sesion.
set -euo pipefail
DESTINO=/var/backups/ebisu
FICHERO="${DESTINO}/ebisu-$(date +%F).tar.gz"
tar -czf "${FICHERO}.tmp" -C /opt/ebisu/var --exclude='bot/ia_config' --exclude='bot/ia_runtime' bot
tar -tzf "${FICHERO}.tmp" > /dev/null   # una copia que no se abre no es una copia
mv "${FICHERO}.tmp" "${FICHERO}"
ls -1t "${DESTINO}"/ebisu-*.tar.gz | tail -n +8 | xargs -r rm -f
