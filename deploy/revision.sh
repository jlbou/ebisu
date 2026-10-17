#!/usr/bin/env bash
# Ebisu - informe de revision del bot en papel (docs/revision-3-dias.md). SOLO LEE: no cambia nada, no avisa a nadie,
# no llama a la IA. La prueba de oro baja los precios de Yahoo a un fichero temporal (no toca los del papel).
#
#   sudo bash /opt/ebisu/deploy/revision.sh [desde AAAA-MM-DD]     (por defecto, 2026-10-15)
set -uo pipefail
DESDE="${1:-2026-10-15}"
APP_DIR=/opt/ebisu
[[ ${EUID} -eq 0 ]] || { echo "hay que lanzarlo con sudo" >&2; exit 1; }
como_ebisu() { sudo -u ebisu env XDG_CACHE_HOME=${APP_DIR}/var/cache bash -c "cd ${APP_DIR} && $*"; }

echo "Revision de Ebisu desde el ${DESDE} ($(date '+%d/%m/%Y %H:%M %Z'))"
echo "== 0. Codigo"
echo "   commit en el VPS: $(sudo -u ebisu git -C "${APP_DIR}" rev-parse --short HEAD)"

como_ebisu ".venv/bin/python -m ebisu.revision --desde ${DESDE}"

echo "== 6. Servicios"
for u in ebisu-comandos ebisu-panel ebisu-dia.timer ebisu-copia.timer; do
    printf '   %-18s %s (reinicios: %s)\n' "${u}" "$(systemctl is-active "${u}")" \
        "$(systemctl show "${u}" -p NRestarts --value 2>/dev/null || echo -)"
done
echo "   avisos y errores en el registro desde el ${DESDE} (sin los de la cache de yfinance):"
journalctl -u ebisu-dia -u ebisu-comandos -u ebisu-panel -u ebisu-copia --since "${DESDE}" -p warning --no-pager -o cat \
    | grep -v -e TzCache -e CookieCache | sort | uniq -c | sort -rn | head -12

echo "== 7. Copias en el VPS (se guardan 7)"
ls -1 /var/backups/ebisu/ 2>/dev/null | sed 's/^/   /'

echo "== 8. Prueba de oro: el papel del bot = el simulador del estudio, con precios reales de hoy"
como_ebisu ".venv/bin/python -m ebisu.prueba_oro" 2>&1 | grep -v -e TzCache -e CookieCache | sed 's/^/   /'

echo "== Falta mirarlo a mano: Healthchecks (ebisu-dia, ebisu-copia, ebisu-copia-portatil en verde) y la copia del portatil"
