#!/usr/bin/env bash
# Ebisu - pasa el codigo a otro commit (el que el propietario apruebe) y reinicia los servicios.
#   sudo bash actualizar.sh <commit-o-etiqueta>
# OJO durante el papel: si cambia ebisu/estrategia.py, el juez lo vera (huella) como incidencia grave (11.2.1).
set -euo pipefail
REF="${1:?uso: sudo bash actualizar.sh <commit-o-etiqueta>}"
[[ ${EUID} -eq 0 ]] || { echo "hay que lanzarlo con sudo" >&2; exit 1; }
sudo -u ebisu git -C /opt/ebisu fetch --quiet --tags origin
sudo -u ebisu git -C /opt/ebisu checkout --quiet --detach "${REF}"
sudo -u ebisu /opt/ebisu/.venv/bin/python -m pip install --quiet -r /opt/ebisu/deploy/requirements-bot.lock
for u in ebisu-dia.service ebisu-dia.timer ebisu-comandos.service ebisu-panel.service ebisu-copia.service ebisu-copia.timer; do
    install -m 644 "/opt/ebisu/deploy/${u}" "/etc/systemd/system/${u}"
done
systemctl daemon-reload
systemctl restart ebisu-comandos.service ebisu-panel.service
sudo -u ebisu bash -c "cd /opt/ebisu && .venv/bin/python -m ebisu.dia --seco"
