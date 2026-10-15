#!/usr/bin/env bash
# Copia diaria en el VPS (la lanza ebisu-copia.service). Guarda las 7 ultimas; el portatil las baja (copia-diaria.ps1).
# Sin el directorio de la IA (ia_config / ia_runtime): no hace falta y podria guardar estado de la sesion.
# Latido a Healthchecks (comprobacion ebisu-copia, HEALTHCHECK_EBISU_COPIA, solo en el .env del VPS): bien -> latido;
# si algo falla -> /fail, que avisa YA. La URL se lee con grep (NUNCA `source .env`) y nunca se imprime.
set -euo pipefail
DESTINO=/var/backups/ebisu
FICHERO="${DESTINO}/ebisu-$(date +%F).tar.gz"
HC_URL="$(grep -E '^HEALTHCHECK_EBISU_COPIA=' /opt/ebisu/.env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '\r"' || true)"
latido() { [[ -z "${HC_URL}" ]] || curl -fsS -m 10 --retry 3 -o /dev/null "${HC_URL}${1:-}" 2>/dev/null \
    || echo "aviso: no se pudo latir a Healthchecks"; }
trap 'latido /fail' ERR

tar -czf "${FICHERO}.tmp" -C /opt/ebisu/var --exclude='bot/ia_config' --exclude='bot/ia_runtime' bot
tar -tzf "${FICHERO}.tmp" > /dev/null   # una copia que no se abre no es una copia
mv "${FICHERO}.tmp" "${FICHERO}"
ls -1t "${DESTINO}"/ebisu-*.tar.gz | tail -n +8 | xargs -r rm -f
latido
