#!/usr/bin/env bash
#
# Ebisu - instala el bot en papel en el VPS, APARTE de Ploutos (P2; docs/plan-bot-papel.md 10, B7).
#
#   sudo bash instalar.sh <commit-o-etiqueta> <usuario-admin>
#
# Idempotente. NO toca nada de Ploutos (ni /opt/ploutos ni sus servicios) y NO pone ningun secreto: el .env lo
# rellena el propietario a mano (/opt/ebisu/.env, permisos 600). <usuario-admin> es el usuario con el que el
# portatil baja las copias por SSH (se le anyade al grupo ebisu-copias, solo lectura de las copias).
#
# Vuelta atras: deploy/desinstalar.sh.

set -euo pipefail
REF="${1:?uso: sudo bash instalar.sh <commit-o-etiqueta> <usuario-admin>}"
ADMIN="${2:?falta el usuario admin que baja las copias}"
APP_DIR=/opt/ebisu
APP_USER=ebisu
REPO=https://github.com/jlbou/ebisu.git
COPIAS=/var/backups/ebisu
VERSION_IA=2.1.266   # ebisu/ia.py VERSION_VERIFICADA

log() { printf '==> %s\n' "$*"; }
avisa() { printf 'AVISO: %s\n' "$*" >&2; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[[ ${EUID} -eq 0 ]] || die "hay que lanzarlo con sudo"
id "${ADMIN}" >/dev/null 2>&1 || die "no existe el usuario ${ADMIN}"

log "Python"
PYVER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
[[ "${PYVER}" == "3.12" ]] || die "se esperaba Python 3.12 y hay ${PYVER}"

log "Usuario ${APP_USER} (sin entrada por consola) y grupo de copias"
id "${APP_USER}" >/dev/null 2>&1 || useradd --system --home-dir "${APP_DIR}" --no-create-home --shell /usr/sbin/nologin "${APP_USER}"
getent group ebisu-copias >/dev/null || groupadd --system ebisu-copias
usermod -aG ebisu-copias "${APP_USER}"
usermod -aG ebisu-copias "${ADMIN}"

log "Codigo (${REF}) en ${APP_DIR}"
install -d -o "${APP_USER}" -g "${APP_USER}" -m 750 "${APP_DIR}"
if [[ ! -d "${APP_DIR}/.git" ]]; then
    sudo -u "${APP_USER}" git clone --quiet "${REPO}" "${APP_DIR}"
fi
sudo -u "${APP_USER}" git -C "${APP_DIR}" fetch --quiet --tags origin
sudo -u "${APP_USER}" git -C "${APP_DIR}" checkout --quiet --detach "${REF}"
install -d -o "${APP_USER}" -g "${APP_USER}" -m 700 "${APP_DIR}/var" "${APP_DIR}/var/bot"
install -d -o "${APP_USER}" -g ebisu-copias -m 750 "${COPIAS}"

log "Entorno de Python con las versiones exactas"
[[ -x "${APP_DIR}/.venv/bin/python" ]] || sudo -u "${APP_USER}" python3 -m venv "${APP_DIR}/.venv"
sudo -u "${APP_USER}" "${APP_DIR}/.venv/bin/python" -m pip install --quiet --upgrade pip
sudo -u "${APP_USER}" "${APP_DIR}/.venv/bin/python" -m pip install --quiet -r "${APP_DIR}/deploy/requirements-bot.lock"

log ".env (lo rellena el propietario; aqui solo se comprueba)"
if [[ ! -f "${APP_DIR}/.env" ]]; then
    install -o "${APP_USER}" -g "${APP_USER}" -m 600 "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    avisa "creado ${APP_DIR}/.env VACIO: rellenalo (sudo nano ${APP_DIR}/.env) y vuelve a lanzar este script"
fi
chown "${APP_USER}:${APP_USER}" "${APP_DIR}/.env"
chmod 600 "${APP_DIR}/.env"
for clave in TELEGRAM_TOKEN TELEGRAM_CHAT_ID HEALTHCHECK_EBISU CLAUDE_CODE_OAUTH_TOKEN; do
    grep -Eq "^${clave}=.+" "${APP_DIR}/.env" || avisa "falta ${clave} en el .env (no se ensenya ningun valor)"
done

log "Copia propia de la IA (${VERSION_IA}) en ${APP_DIR}/bin"
bash "${APP_DIR}/deploy/instalar-ia.sh"

log "Comprobaciones"
tailscale ip -4 >/dev/null 2>&1 || avisa "Tailscale no da IP: el panel no arrancara hasta que la de"

log "Servicios (solo los de Ebisu)"
for u in ebisu-dia.service ebisu-dia.timer ebisu-comandos.service ebisu-panel.service ebisu-copia.service ebisu-copia.timer; do
    install -m 644 "${APP_DIR}/deploy/${u}" "/etc/systemd/system/${u}"
done
systemctl daemon-reload
systemctl enable --now ebisu-dia.timer ebisu-copia.timer >/dev/null
systemctl enable ebisu-comandos.service ebisu-panel.service >/dev/null
systemctl restart ebisu-comandos.service ebisu-panel.service

log "Prueba en seco (sin Telegram, sin latido, sin guardar)"
sudo -u "${APP_USER}" bash -c "cd ${APP_DIR} && .venv/bin/python -m ebisu.dia --seco"

log "Hecho. Siguiente (decide el propietario): un mensaje de prueba, 3 dias sin incidencias y despues"
log "  sudo -u ${APP_USER} bash -c 'cd ${APP_DIR} && .venv/bin/python -m ebisu.dia --empezar AAAA-MM-DD'"
