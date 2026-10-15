#!/usr/bin/env bash
#
# Ebisu - copia PROPIA del programa de la IA en /opt/ebisu/bin (decision del propietario, 15/10/2026, opcion A).
#
#   sudo bash /opt/ebisu/deploy/instalar-ia.sh      (lo lanza instalar.sh; idempotente)
#
# Adaptado de deploy/install-claude.sh de Ploutos (solo lectura de Ploutos). Lo que hace, y por que:
# 1. La version VERIFICADA, fija (ebisu/ia.py VERSION_VERIFICADA; hay prueba que lo comprueba).
# 2. Baja el binario directamente de la web oficial de versiones (sin el instalador, que escribe en la casa del
#    usuario) y lo comprueba contra el manifiesto FIRMADO por Anthropic (huella de la clave fijada aqui). Un binario
#    que no cuadra se borra y el script para.
# 3. Lo deja en /opt/ebisu/bin, de root y solo lectura para el bot: el bot no lo puede cambiar, y no depende de
#    ninguna otra instalacion de la maquina.
# NO pone el token: CLAUDE_CODE_OAUTH_TOKEN lo pone el propietario a mano en /opt/ebisu/.env.

set -euo pipefail

VERSION_IA="2.1.266"
PLATAFORMA="linux-x64"
# Huella de "Anthropic Claude Code Release Signing <security@anthropic.com>" (code.claude.com/docs/en/setup,
# comprobada el 23/09/2026 al instalar la primera vez).
HUELLA_FIRMA="31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE"
VERSIONES="https://downloads.claude.ai/claude-code-releases"
APP_DIR=/opt/ebisu
APP_USER=ebisu
BIN_DIR="${APP_DIR}/bin"
BIN="${BIN_DIR}/claude-${VERSION_IA}"
ENLACE="${BIN_DIR}/claude"

log() { printf '==> %s\n' "$*"; }
avisa() { printf 'AVISO: %s\n' "$*" >&2; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[[ ${EUID} -eq 0 ]] || die "hay que lanzarlo con sudo"
[[ "$(uname -m)" == "x86_64" ]] || die "se esperaba x86_64 (${PLATAFORMA}) y es $(uname -m)"
for p in curl gpg sha256sum python3; do command -v "${p}" >/dev/null || die "falta ${p}"; done

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

log "Manifiesto firmado de la ${VERSION_IA}"
export GNUPGHOME="${TMP}/gnupg"
install -d -m 700 "${GNUPGHOME}"
curl -fsSL https://downloads.claude.ai/keys/claude-code.asc -o "${TMP}/clave.asc"
gpg --batch --quiet --import "${TMP}/clave.asc"
HUELLAS="$(gpg --batch --with-colons --fingerprint | awk -F: '/^fpr:/ {print $10}')"
grep -qx "${HUELLA_FIRMA}" <<<"${HUELLAS}" || die "la clave descargada NO es la de Anthropic (${HUELLAS})"
curl -fsSL "${VERSIONES}/${VERSION_IA}/manifest.json" -o "${TMP}/manifest.json"
curl -fsSL "${VERSIONES}/${VERSION_IA}/manifest.json.sig" -o "${TMP}/manifest.json.sig"
# La salida de gpg se guarda ANTES de buscar en ella: con `gpg | grep -q` y pipefail, una firma valida podia dar
# "no valida" (SIGPIPE, codigo 141; visto en Ploutos el 23/09/2026).
ESTADO_GPG="$(gpg --batch --status-fd 1 --verify "${TMP}/manifest.json.sig" "${TMP}/manifest.json" 2>/dev/null)" \
    || die "gpg no pudo verificar la firma del manifiesto"
grep -q "^\[GNUPG:\] VALIDSIG ${HUELLA_FIRMA} " <<<"${ESTADO_GPG}" || die "la firma del manifiesto NO es de Anthropic"
ESPERADO="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["platforms"][sys.argv[2]]["checksum"])' \
    "${TMP}/manifest.json" "${PLATAFORMA}")"
[[ "${ESPERADO}" =~ ^[0-9a-f]{64}$ ]] || die "el manifiesto no trae un sha256 para ${PLATAFORMA}"

install -d -o root -g "${APP_USER}" -m 750 "${BIN_DIR}"
if [[ -f "${BIN}" ]] && [[ "$(sha256sum "${BIN}" | cut -d' ' -f1)" == "${ESPERADO}" ]]; then
    log "La ${VERSION_IA} ya esta en ${BIN} y cuadra con el manifiesto"
else
    log "Bajando la ${VERSION_IA} (${PLATAFORMA})"
    curl -fsSL "${VERSIONES}/${VERSION_IA}/${PLATAFORMA}/claude" -o "${TMP}/claude"
    REAL="$(sha256sum "${TMP}/claude" | cut -d' ' -f1)"
    [[ "${REAL}" == "${ESPERADO}" ]] || die "el binario NO cuadra con el manifiesto firmado (${REAL} != ${ESPERADO})"
    install -o root -g "${APP_USER}" -m 750 "${TMP}/claude" "${BIN}"
fi
ln -sfn "${BIN}" "${ENLACE}"

chmod 711 "${TMP}"
install -d -o "${APP_USER}" -g "${APP_USER}" -m 700 "${TMP}/casa"   # una casa de usar y tirar para la prueba
SALIDA="$(sudo -u "${APP_USER}" env HOME="${TMP}/casa" DISABLE_UPDATES=1 "${ENLACE}" --version)"
[[ "${SALIDA}" == "${VERSION_IA} "* ]] || die "la IA dice '${SALIDA}', se esperaba ${VERSION_IA}"
log "OK: ${ENLACE} -> ${BIN} (${SALIDA})"
