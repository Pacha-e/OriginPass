#!/usr/bin/env bash
# Updates OriginPass on the EC2 instance to the head of main.
# Order matters: code, dependencies, stop, migrations, static files, start, then a check
# over HTTPS through the local nginx. A failed step stops the script.
# Usage (on the instance):
#   sudo bash /opt/originpass/app/deploy/aws/actualizar-ec2.sh 44-206-186-9.sslip.io
set -euo pipefail

HOST_PUBLICO="${1:?Falta el nombre publico, por ejemplo 44-206-186-9.sslip.io}"
APP_DIR=/opt/originpass/app
VENV=/opt/originpass/venv
LOCK=/run/originpass-update.lock

[[ "$(id -u)" -eq 0 ]] || { echo "Ejecuta con sudo"; exit 1; }

# One update at a time.
exec 9>"$LOCK"
flock -n 9 || { echo "Otra actualizacion esta en curso"; exit 1; }

echo ">> Codigo"
sudo -u originpass git -C "$APP_DIR" pull --ff-only

echo ">> Dependencias"
"$VENV/bin/pip" install -q -r "$APP_DIR/requirements.txt"

# The environment file is readable by root only, so the manage.py steps run as root.
set -a
. /etc/originpass.env
set +a
cd "$APP_DIR"

# Some migrations rewrite existing rows (0013 re-signs custody, 0014 closes open
# offers). The old code must not write while they run, so the site stops first.
echo ">> Detener el servicio"
systemctl stop originpass
# If a step below fails the site stays stopped: the old code may not match a
# schema some migrations already changed. Fix, then run this script again.

echo ">> Migraciones"
"$VENV/bin/python" manage.py migrate --noinput

echo ">> Archivos estaticos"
"$VENV/bin/python" manage.py collectstatic --noinput
chown -R originpass:originpass "$APP_DIR" "$VENV"

echo ">> Arranque"
systemctl start originpass
sleep 3

echo ">> Comprobacion"
# Through local nginx on 443, with the certificate checked (no -k).
codigo="$(curl -s -o /dev/null -w '%{http_code}' \
  --resolve "${HOST_PUBLICO}:443:127.0.0.1" \
  "https://${HOST_PUBLICO}/healthz/" || true)"
echo "healthz: ${codigo}"
if [[ "$codigo" != "200" ]]; then
  echo "El sitio no responde bien: revisa journalctl -u originpass y el certificado"
  exit 1
fi

echo "Listo. Commit: $(sudo -u originpass git -C "$APP_DIR" log --oneline -1)"
