#!/usr/bin/env bash
# Ebisu - vuelta atras: para y quita SOLO lo de Ebisu. Ploutos no se toca en ningun paso.
#   sudo bash desinstalar.sh            (deja /opt/ebisu y las copias)
#   sudo bash desinstalar.sh --borrar   (borra tambien /opt/ebisu y /var/backups/ebisu; pide confirmacion)
set -euo pipefail
[[ ${EUID} -eq 0 ]] || { echo "hay que lanzarlo con sudo" >&2; exit 1; }
for u in ebisu-dia.timer ebisu-copia.timer ebisu-comandos.service ebisu-panel.service ebisu-dia.service ebisu-copia.service; do
    systemctl disable --now "${u}" 2>/dev/null || true
    rm -f "/etc/systemd/system/${u}"
done
systemctl daemon-reload
echo "Servicios de Ebisu parados y quitados."
if [[ "${1:-}" == "--borrar" ]]; then
    read -r -p "Borrar /opt/ebisu (codigo, .env, papel) y /var/backups/ebisu? Escribe BORRAR: " r
    [[ "${r}" == "BORRAR" ]] || { echo "No se borra nada."; exit 0; }
    rm -rf /opt/ebisu /var/backups/ebisu
    userdel ebisu 2>/dev/null || true
    groupdel ebisu-copias 2>/dev/null || true
    echo "Borrado."
fi
