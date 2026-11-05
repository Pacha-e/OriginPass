#!/usr/bin/env bash
# Actualiza OriginPass en la instancia EC2 con el código de main.
# Hace los tres pasos que hacen falta después de cada cambio: código nuevo,
# archivos estáticos (collectstatic) y reinicio del servicio. Sin collectstatic el
# sitio sigue sirviendo los JavaScript y CSS viejos.
# Uso (en la instancia): sudo bash /opt/originpass/app/deploy/aws/actualizar-ec2.sh 13-220-96-49.sslip.io
set -euo pipefail

HOST_PUBLICO="${1:?Falta el nombre publico, por ejemplo 13-220-96-49.sslip.io}"
APP_DIR=/opt/originpass/app
[[ "$(id -u)" -eq 0 ]] || { echo "Ejecuta con sudo"; exit 1; }

echo ">> Codigo"
sudo -u originpass git -C "$APP_DIR" pull --ff-only
echo ">> Archivos estaticos"
set -a
. /etc/originpass.env
set +a
cd "$APP_DIR"
/opt/originpass/venv/bin/python manage.py collectstatic --noinput
echo ">> Reinicio"
systemctl restart originpass
sleep 3
echo ">> Comprobacion"
codigo="$(curl -sk -o /dev/null -w '%{http_code}' --resolve "${HOST_PUBLICO}:443:127.0.0.1" "https://${HOST_PUBLICO}/healthz/" || true)"
echo "healthz: ${codigo}"
[[ "$codigo" == "200" ]] || { echo "El sitio no responde bien: revisa journalctl -u originpass"; exit 1; }
echo "Listo. Commit: $(sudo -u originpass git -C "$APP_DIR" log --oneline -1)"
